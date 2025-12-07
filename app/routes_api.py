from datetime import date
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from . import db
from .models import User, Scholarship, Application, Finance
from .utils import check_password

api_bp = Blueprint("api", __name__)


@api_bp.post("/login")
def api_login():
	data = request.get_json(force=True, silent=True) or {}
	email = (data.get("email") or "").lower().strip()
	password = data.get("password") or ""
	user = db.session.query(User).filter_by(email=email).first()
	if not user or not check_password(password, user.password_hash):
		return jsonify({"ok": False, "error": "invalid_credentials"}), 401
	return jsonify({"ok": True, "user": {"id": user.user_id, "role": user.role, "name": user.name}})


@api_bp.get("/scholarships")
@login_required
def api_scholarships():
	items = db.session.query(Scholarship).all()
	return jsonify([
		{
			"scholarship_id": s.scholarship_id,
			"name": s.name,
			"category": s.category,
			"eligibility": s.eligibility,
			"amount": s.amount,
			"start_date": s.start_date.isoformat(),
			"end_date": s.end_date.isoformat(),
		}
		for s in items
	])


@api_bp.post("/scholarships")
@login_required
def api_create_scholarship():
	if current_user.role != "admin":
		return jsonify({"ok": False, "error": "forbidden"}), 403
	data = request.get_json(force=True, silent=True) or {}
	name = (data.get("name") or "").strip()
	category = (data.get("category") or "").strip()
	eligibility = (data.get("eligibility") or "").strip()
	amount = float(data.get("amount") or 0)
	start_date = data.get("start_date")
	end_date = data.get("end_date")
	min_cgpa = data.get("min_cgpa")
	income_limit = data.get("income_limit")
	if not (name and category and eligibility and start_date and end_date and amount > 0):
		return jsonify({"ok": False, "error": "missing_or_invalid_fields"}), 400
	try:
		start_d = date.fromisoformat(start_date)
		end_d = date.fromisoformat(end_date)
	except Exception:
		return jsonify({"ok": False, "error": "invalid_date_format"}), 400
	sch = Scholarship(
		name=name,
		category=category,
		eligibility=eligibility,
		amount=amount,
		start_date=start_d,
		end_date=end_d,
		min_cgpa=float(min_cgpa) if min_cgpa is not None else None,
		income_limit=float(income_limit) if income_limit is not None else None,
	)
	db.session.add(sch)
	db.session.commit()
	return jsonify({"ok": True, "scholarship_id": sch.scholarship_id})


@api_bp.post("/apply")
@login_required
def api_apply():
	data = request.get_json(force=True, silent=True) or {}
	sch_id = int(data.get("scholarship_id"))
	cgpa_value = float(data.get("cgpa")) if data.get("cgpa") is not None else None

	# duplicate check
	exists = db.session.query(Application).filter_by(student_id=current_user.user_id, scholarship_id=sch_id).first()
	if exists:
		return jsonify({"ok": False, "error": "duplicate"}), 400

	app = Application(student_id=current_user.user_id, scholarship_id=sch_id, cgpa_value=cgpa_value)
	db.session.add(app)
	db.session.commit()
	return jsonify({"ok": True, "application_id": app.application_id})


@api_bp.post("/approve")
@login_required
def api_approve():
	if current_user.role != "admin":
		return jsonify({"ok": False, "error": "forbidden"}), 403
	data = request.get_json(force=True, silent=True) or {}
	app_id = int(data.get("application_id"))
	status = data.get("status")
	remarks = data.get("remarks")
	app = db.session.get(Application, app_id)
	if not app:
		return jsonify({"ok": False, "error": "not_found"}), 404
	if status not in {"approved", "rejected"}:
		return jsonify({"ok": False, "error": "invalid_status"}), 400
	app.status = status
	app.remarks = remarks
	app.reviewed_by = current_user.user_id
	if status == "approved":
		fund = db.session.query(Finance).filter_by(year=date.today().year).first()
		if fund:
			fund.allocated_amount += float(app.scholarship.amount)
			fund.recalc()
	db.session.commit()
	return jsonify({"ok": True})


@api_bp.get("/fund-report/year")
@login_required
def api_fund_report_year():
	year = int(request.args.get("year", date.today().year))
	fund = db.session.query(Finance).filter_by(year=year).first()
	if not fund:
		return jsonify({"year": year, "budget": 0, "allocated": 0, "balance": 0})
	return jsonify({"year": year, "budget": fund.budget_amount, "allocated": fund.allocated_amount, "balance": fund.balance_amount})
