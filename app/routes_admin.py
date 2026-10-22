from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from . import db
from .models import Scholarship, Application, User, Finance
from .services import decide_application
from .utils import role_required, parse_float, parse_int

admin_bp = Blueprint("admin", __name__, template_folder="templates")

CATEGORIES = ["merit", "financial", "minority", "sports"]


@admin_bp.get("/dashboard")
@login_required
@role_required("admin")
def dashboard():
	total_students = db.session.query(User).filter_by(role="student").count()
	pending = db.session.query(Application).filter_by(status="pending").count()
	approved = db.session.query(Application).filter_by(status="approved").count()
	rejected = db.session.query(Application).filter_by(status="rejected").count()

	# charts data
	by_category = dict(
		db.session.query(Scholarship.category, func.count(Scholarship.scholarship_id))
		.group_by(Scholarship.category).all()
	)
	by_department = {}
	for dept, count in (
		db.session.query(User.department, func.count(Application.application_id))
		.join(Application, Application.student_id == User.user_id)
		.filter(User.role == "student")
		.group_by(User.department)
		.all()
	):
		# Students without a department would produce a null key and break tojson's key sorting
		label = dept or "Unassigned"
		by_department[label] = by_department.get(label, 0) + count

	fund = db.session.query(Finance).filter_by(year=date.today().year).first()

	# recent lists
	def recent(status: str):
		return (
			db.session.query(Application)
			.filter_by(status=status)
			.order_by(Application.submitted_date.desc())
			.limit(5)
			.all()
		)

	return render_template(
		"admin/dashboard.html",
		total_students=total_students,
		pending=pending,
		approved=approved,
		rejected=rejected,
		by_category=by_category,
		by_department=by_department,
		fund=fund,
		pending_items=recent("pending"),
		approved_items=recent("approved"),
		rejected_items=recent("rejected"),
	)


# Students list
@admin_bp.get("/students")
@login_required
@role_required("admin")
def students():
	items = db.session.query(User).filter_by(role="student").order_by(User.name.asc()).all()
	return render_template("admin/students.html", items=items)


# Scholarships CRUD
@admin_bp.get("/scholarships")
@login_required
@role_required("admin")
def scholarships_list():
	items = db.session.query(Scholarship).order_by(Scholarship.end_date.desc()).all()
	return render_template("admin/scholarships.html", items=items, categories=CATEGORIES)


@admin_bp.post("/scholarships")
@login_required
@role_required("admin")
def scholarships_create():
	name = request.form.get("name", "").strip()
	category = request.form.get("category", "").strip()
	eligibility = request.form.get("eligibility", "").strip()
	try:
		if not (name and eligibility):
			raise ValueError("Name and eligibility are required.")
		if category not in CATEGORIES:
			raise ValueError("Choose a valid category.")
		amount = parse_float(request.form.get("amount"), "Amount", 1)
		if amount is None:
			raise ValueError("Amount is required.")
		min_cgpa = parse_float(request.form.get("min_cgpa"), "Min CGPA", 0, 10)
		income_limit = parse_float(request.form.get("income_limit"), "Income limit", 0)
		try:
			start_date_val = date.fromisoformat(request.form.get("start_date", ""))
			end_date_val = date.fromisoformat(request.form.get("end_date", ""))
		except ValueError:
			raise ValueError("Invalid date format. Use YYYY-MM-DD.")
		if end_date_val < start_date_val:
			raise ValueError("End date must be on or after the start date.")
	except ValueError as e:
		flash(str(e), "danger")
		return redirect(url_for("admin.scholarships_list"))
	item = Scholarship(
		name=name,
		category=category,
		eligibility=eligibility,
		amount=amount,
		start_date=start_date_val,
		end_date=end_date_val,
		min_cgpa=min_cgpa,
		income_limit=income_limit,
	)
	db.session.add(item)
	db.session.commit()
	flash("Scholarship created", "success")
	return redirect(url_for("admin.scholarships_list"))


@admin_bp.post("/scholarships/<int:scholarship_id>/delete")
@login_required
@role_required("admin")
def scholarships_delete(scholarship_id: int):
	item = db.session.get(Scholarship, scholarship_id)
	if item:
		# Deleting would cascade away approved applications whose money is already allocated
		if any(a.status == "approved" for a in item.applications):
			flash("Cannot delete a scholarship that has approved applications.", "danger")
			return redirect(url_for("admin.scholarships_list"))
		db.session.delete(item)
		db.session.commit()
		flash("Scholarship deleted", "success")
	return redirect(url_for("admin.scholarships_list"))


# Applications review
@admin_bp.get("/applications")
@login_required
@role_required("admin")
def applications():
	status = request.args.get("status")
	q = db.session.query(Application)
	if status in {"pending", "approved", "rejected"}:
		q = q.filter(Application.status == status)
	else:
		status = None
	items = q.order_by(Application.submitted_date.desc()).all()
	return render_template("admin/applications.html", items=items, status=status)


@admin_bp.post("/applications/<int:application_id>/decision")
@login_required
@role_required("admin")
def application_decision(application_id: int):
	app = db.session.get(Application, application_id)
	if not app:
		flash("Application not found", "danger")
		return redirect(url_for("admin.applications"))
	error = decide_application(app, request.form.get("status", ""), request.form.get("remarks"), current_user)
	if error:
		flash(error, "danger")
	else:
		flash("Decision recorded", "success")
	# Return to the page the decision was made from
	if request.form.get("next") == "dashboard":
		return redirect(url_for("admin.dashboard"))
	return redirect(url_for("admin.applications", status=request.form.get("filter") or None))


# Finance management
@admin_bp.get("/finance")
@login_required
@role_required("admin")
def finance():
	items = db.session.query(Finance).order_by(Finance.year.desc()).all()
	return render_template("admin/finance.html", items=items, current_year=date.today().year)


@admin_bp.post("/finance")
@login_required
@role_required("admin")
def finance_save():
	try:
		year = parse_int(request.form.get("year"), "Year")
		if not 2000 <= year <= 2100:
			raise ValueError("Year must be between 2000 and 2100.")
		budget = parse_float(request.form.get("budget_amount"), "Budget", 0)
		if budget is None:
			raise ValueError("Budget is required.")
	except ValueError as e:
		flash(str(e), "danger")
		return redirect(url_for("admin.finance"))
	item = db.session.query(Finance).filter_by(year=year).first()
	if not item:
		item = Finance(year=year, budget_amount=budget, allocated_amount=0)
		db.session.add(item)
	else:
		if budget < float(item.allocated_amount or 0):
			flash(f"Budget cannot be lower than the ₹{item.allocated_amount:,.0f} already allocated.", "danger")
			return redirect(url_for("admin.finance"))
		item.budget_amount = budget
	item.recalc()
	db.session.commit()
	flash("Finance updated", "success")
	return redirect(url_for("admin.finance"))
