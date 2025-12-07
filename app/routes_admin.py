from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from . import db
from .models import Scholarship, Application, User, Finance
from .utils import role_required

admin_bp = Blueprint("admin", __name__, template_folder="templates")


@admin_bp.get("/dashboard")
@login_required
@role_required("admin")
def dashboard():
	total_students = db.session.query(User).filter_by(role="student").count()
	pending = db.session.query(Application).filter_by(status="pending").count()
	approved = db.session.query(Application).filter_by(status="approved").count()
	rejected = db.session.query(Application).filter_by(status="rejected").count()
	total_allocated = db.session.query(func.coalesce(func.sum(Scholarship.amount), 0)).join(Application, Application.scholarship_id == Scholarship.scholarship_id).filter(Application.status == "approved").scalar() or 0

	# charts data
	by_category = dict(
		db.session.query(Scholarship.category, func.count(Scholarship.scholarship_id))
		.group_by(Scholarship.category).all()
	)
	by_department = dict(
		db.session.query(User.department, func.count(Application.application_id))
		.join(Application, Application.student_id == User.user_id)
		.filter(User.role == "student")
		.group_by(User.department)
		.all()
	)

	fund = db.session.query(Finance).filter_by(year=date.today().year).first()

	# recent lists
	pending_items = (
		db.session.query(Application)
		.filter_by(status="pending")
		.order_by(Application.submitted_date.desc())
		.limit(5)
		.all()
	)
	approved_items = (
		db.session.query(Application)
		.filter_by(status="approved")
		.order_by(Application.submitted_date.desc())
		.limit(5)
		.all()
	)
	rejected_items = (
		db.session.query(Application)
		.filter_by(status="rejected")
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
		total_allocated=total_allocated,
		by_category=by_category,
		by_department=by_department,
		fund=fund,
		pending_items=pending_items,
		approved_items=approved_items,
		rejected_items=rejected_items,
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
	return render_template("admin/scholarships.html", items=items)


@admin_bp.post("/scholarships")
@login_required
@role_required("admin")
def scholarships_create():
	name = request.form.get("name")
	category = request.form.get("category")
	eligibility = request.form.get("eligibility")
	amount = float(request.form.get("amount") or 0)
	start_date_str = request.form.get("start_date")
	end_date_str = request.form.get("end_date")
	min_cgpa = request.form.get("min_cgpa")
	income_limit = request.form.get("income_limit")
	try:
		start_date_val = date.fromisoformat(start_date_str)
		end_date_val = date.fromisoformat(end_date_str)
	except Exception:
		flash("Invalid date format. Use YYYY-MM-DD.", "danger")
		return redirect(url_for("admin.scholarships_list"))
	item = Scholarship(
		name=name,
		category=category,
		eligibility=eligibility,
		amount=amount,
		start_date=start_date_val,
		end_date=end_date_val,
		min_cgpa=float(min_cgpa) if min_cgpa else None,
		income_limit=float(income_limit) if income_limit else None,
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
	q = q.order_by(Application.submitted_date.desc()).all()
	return render_template("admin/applications.html", items=q, status=status)


@admin_bp.post("/applications/<int:application_id>/decision")
@login_required
@role_required("admin")
def application_decision(application_id: int):
	status = request.form.get("status")
	remarks = request.form.get("remarks")
	app = db.session.get(Application, application_id)
	if not app:
		flash("Application not found", "danger")
		return redirect(url_for("admin.applications"))
	if status not in {"approved", "rejected"}:
		flash("Invalid status", "warning")
		return redirect(url_for("admin.applications"))
	app.status = status
	app.remarks = remarks
	app.reviewed_by = current_user.user_id
	# Update finance allocated when approved
	if status == "approved":
		from .models import Finance
		fund = db.session.query(Finance).filter_by(year=date.today().year).first()
		if fund:
			fund.allocated_amount += float(app.scholarship.amount)
			fund.recalc()
	db.session.commit()
	flash("Decision recorded", "success")
	# Redirect back to dashboard if the action came from quick actions
	ref = request.headers.get("Referer", "")
	if "/admin/dashboard" in ref:
		return redirect(url_for("admin.dashboard"))
	return redirect(url_for("admin.applications"))


# Finance management
@admin_bp.get("/finance")
@login_required
@role_required("admin")
def finance():
	items = db.session.query(Finance).order_by(Finance.year.desc()).all()
	return render_template("admin/finance.html", items=items)


@admin_bp.post("/finance")
@login_required
@role_required("admin")
def finance_save():
	year = int(request.form.get("year"))
	budget = float(request.form.get("budget_amount") or 0)
	item = db.session.query(Finance).filter_by(year=year).first()
	if not item:
		item = Finance(year=year, budget_amount=budget, allocated_amount=0)
		db.session.add(item)
	else:
		item.budget_amount = budget
	item.recalc()
	db.session.commit()
	flash("Finance updated", "success")
	return redirect(url_for("admin.finance"))
