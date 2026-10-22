from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, login_user
from sqlalchemy.exc import IntegrityError
from . import db
from .models import User, Scholarship, Application, Finance
from .services import decide_application, eligibility_error
from .utils import check_password, parse_float, parse_int

api_bp = Blueprint("api", __name__)


def _json_body():
	# Requiring a real JSON content type stops cross-site form posts (a CSRF vector for
	# cookie-authenticated endpoints), because browsers cannot send it cross-origin
	# without a CORS preflight.
	if not request.is_json:
		return None
	data = request.get_json(silent=True)
	return data if isinstance(data, dict) else None


def _error(code: str, status: int, message: str | None = None):
	body = {"ok": False, "error": code}
	if message:
		body["message"] = message
	return jsonify(body), status


@api_bp.before_request
def require_json_for_writes():
	if request.method == "POST" and _json_body() is None:
		return _error("expected_json", 415, "Send a JSON object with Content-Type: application/json")


@api_bp.errorhandler(401)
def unauthorized(e):
	return _error("unauthorized", 401)


@api_bp.post("/login")
def api_login():
	data = _json_body()
	email = (data.get("email") or "").lower().strip()
	password = data.get("password") or ""
	user = db.session.query(User).filter_by(email=email).first()
	if not user or not check_password(password, user.password_hash):
		return _error("invalid_credentials", 401)
	login_user(user)
	return jsonify({"ok": True, "user": {"id": user.user_id, "role": user.role, "name": user.name}})


@api_bp.get("/scholarships")
@login_required
def api_scholarships():
	items = db.session.query(Scholarship).order_by(Scholarship.end_date.asc()).all()
	return jsonify([
		{
			"scholarship_id": s.scholarship_id,
			"name": s.name,
			"category": s.category,
			"eligibility": s.eligibility,
			"amount": s.amount,
			"start_date": s.start_date.isoformat(),
			"end_date": s.end_date.isoformat(),
			"min_cgpa": s.min_cgpa,
			"income_limit": s.income_limit,
		}
		for s in items
	])


@api_bp.post("/scholarships")
@login_required
def api_create_scholarship():
	if current_user.role != "admin":
		return _error("forbidden", 403)
	data = _json_body()
	name = (data.get("name") or "").strip()
	category = (data.get("category") or "").strip()
	eligibility = (data.get("eligibility") or "").strip()
	try:
		amount = parse_float(data.get("amount"), "amount", 1)
		min_cgpa = parse_float(data.get("min_cgpa"), "min_cgpa", 0, 10)
		income_limit = parse_float(data.get("income_limit"), "income_limit", 0)
	except ValueError as e:
		return _error("missing_or_invalid_fields", 400, str(e))
	start_date = data.get("start_date")
	end_date = data.get("end_date")
	if not (name and category and eligibility and start_date and end_date and amount):
		return _error("missing_or_invalid_fields", 400)
	try:
		start_d = date.fromisoformat(start_date)
		end_d = date.fromisoformat(end_date)
	except (TypeError, ValueError):
		return _error("invalid_date_format", 400)
	if end_d < start_d:
		return _error("invalid_date_range", 400)
	sch = Scholarship(
		name=name,
		category=category,
		eligibility=eligibility,
		amount=amount,
		start_date=start_d,
		end_date=end_d,
		min_cgpa=min_cgpa,
		income_limit=income_limit,
	)
	db.session.add(sch)
	db.session.commit()
	return jsonify({"ok": True, "scholarship_id": sch.scholarship_id}), 201


@api_bp.post("/apply")
@login_required
def api_apply():
	if current_user.role != "student":
		return _error("forbidden", 403)
	data = _json_body()
	try:
		sch_id = parse_int(data.get("scholarship_id"), "scholarship_id")
		cgpa_value = parse_float(data.get("cgpa"), "cgpa", 0, 10)
	except ValueError as e:
		return _error("missing_or_invalid_fields", 400, str(e))
	sch = db.session.get(Scholarship, sch_id)
	if not sch:
		return _error("not_found", 404)
	error = eligibility_error(current_user, sch, cgpa_value)
	if error == "You have already applied.":
		return _error("duplicate", 409, error)
	if error:
		return _error("not_eligible", 400, error)

	app = Application(student_id=current_user.user_id, scholarship_id=sch_id, cgpa_value=cgpa_value)
	db.session.add(app)
	try:
		db.session.commit()
	except IntegrityError:
		db.session.rollback()
		return _error("duplicate", 409)
	return jsonify({"ok": True, "application_id": app.application_id}), 201


@api_bp.post("/approve")
@login_required
def api_approve():
	if current_user.role != "admin":
		return _error("forbidden", 403)
	data = _json_body()
	try:
		app_id = parse_int(data.get("application_id"), "application_id")
	except ValueError as e:
		return _error("missing_or_invalid_fields", 400, str(e))
	app = db.session.get(Application, app_id)
	if not app:
		return _error("not_found", 404)
	error = decide_application(app, data.get("status") or "", data.get("remarks"), current_user)
	if error:
		return _error("decision_rejected", 400, error)
	return jsonify({"ok": True})


@api_bp.get("/fund-report/year")
@login_required
def api_fund_report_year():
	if current_user.role != "admin":
		return _error("forbidden", 403)
	try:
		year = parse_int(request.args.get("year", date.today().year), "year")
	except ValueError as e:
		return _error("invalid_year", 400, str(e))
	fund = db.session.query(Finance).filter_by(year=year).first()
	if not fund:
		return jsonify({"year": year, "budget": 0, "allocated": 0, "balance": 0})
	return jsonify({"year": year, "budget": fund.budget_amount, "allocated": fund.allocated_amount, "balance": fund.balance_amount})
