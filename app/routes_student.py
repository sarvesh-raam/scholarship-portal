from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from . import db
from .models import Scholarship, Application
from .utils import role_required, save_uploaded

student_bp = Blueprint("student", __name__, template_folder="templates")


@student_bp.get("/dashboard")
@login_required
@role_required("student")
def dashboard():
	apps = (
		db.session.query(Application)
		.filter(Application.student_id == current_user.user_id)
		.order_by(Application.submitted_date.desc())
		.all()
	)
	return render_template("student/dashboard.html", applications=apps)


@student_bp.get("/scholarships")
@login_required
@role_required("student")
def scholarships():
	today = date.today()
	items = (
		db.session.query(Scholarship)
		.filter(Scholarship.start_date <= today, Scholarship.end_date >= today)
		.order_by(Scholarship.end_date.asc())
		.all()
	)
	return render_template("student/scholarships.html", items=items)


@student_bp.post("/apply/<int:scholarship_id>")
@login_required
@role_required("student")
def apply(scholarship_id: int):
	sch = db.session.get(Scholarship, scholarship_id)
	if not sch:
		flash("Scholarship not found", "danger")
		return redirect(url_for("student.scholarships"))
	# Prevent duplicate
	existing = (
		db.session.query(Application)
		.filter_by(student_id=current_user.user_id, scholarship_id=scholarship_id)
		.first()
	)
	if existing:
		flash("You have already applied.", "warning")
		return redirect(url_for("student.scholarships"))

	cgpa_value = float(request.form.get("cgpa")) if request.form.get("cgpa") else None
	income_path = save_uploaded(request.files.get("income_proof"), f"user_{current_user.user_id}") if request.files else ""
	govt_id_path = save_uploaded(request.files.get("govt_id"), f"user_{current_user.user_id}") if request.files else ""

	# Basic validation against scholarship thresholds
	if sch.min_cgpa is not None and (cgpa_value or 0) < sch.min_cgpa:
		flash("CGPA below required minimum.", "danger")
		return redirect(url_for("student.scholarships"))
	# Only block on income if the student's profile has a value set
	if sch.income_limit is not None and current_user.family_income is not None:
		if float(current_user.family_income) > float(sch.income_limit):
			flash("Family income exceeds limit.", "danger")
			return redirect(url_for("student.scholarships"))

	app = Application(
		student_id=current_user.user_id,
		scholarship_id=scholarship_id,
		cgpa_value=cgpa_value,
		income_proof_path=income_path,
		govt_id_path=govt_id_path,
	)
	db.session.add(app)
	db.session.commit()
	flash("Application submitted.", "success")
	return redirect(url_for("student.dashboard"))


@student_bp.get("/profile")
@login_required
@role_required("student")
def profile():
	return render_template("student/profile.html")


@student_bp.post("/profile")
@login_required
@role_required("student")
def profile_post():
	current_user.name = request.form.get("name", current_user.name)
	current_user.department = request.form.get("department")
	cgpa = request.form.get("cgpa")
	income = request.form.get("family_income")
	current_user.cgpa = float(cgpa) if cgpa else current_user.cgpa
	current_user.family_income = float(income) if income else current_user.family_income
	db.session.commit()
	flash("Profile updated", "success")
	return redirect(url_for("student.profile"))
