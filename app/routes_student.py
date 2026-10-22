import os
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Scholarship, Application
from .services import eligibility_error
from .utils import role_required, save_uploaded, parse_float, has_upload, validate_upload

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
	applied_ids = {
		sid for (sid,) in db.session.query(Application.scholarship_id).filter_by(student_id=current_user.user_id)
	}
	return render_template("student/scholarships.html", items=items, applied_ids=applied_ids)


@student_bp.post("/apply/<int:scholarship_id>")
@login_required
@role_required("student")
def apply(scholarship_id: int):
	sch = db.session.get(Scholarship, scholarship_id)
	if not sch:
		flash("Scholarship not found", "danger")
		return redirect(url_for("student.scholarships"))

	income_file = request.files.get("income_proof")
	govt_id_file = request.files.get("govt_id")
	try:
		cgpa_value = parse_float(request.form.get("cgpa"), "CGPA", 0, 10)
		if not (has_upload(income_file) and has_upload(govt_id_file)):
			raise ValueError("Both income proof and government ID documents are required.")
		validate_upload(income_file)
		validate_upload(govt_id_file)
	except ValueError as e:
		flash(str(e), "danger")
		return redirect(url_for("student.scholarships"))

	# Validate eligibility before writing any files to disk
	error = eligibility_error(current_user, sch, cgpa_value)
	if error:
		flash(error, "warning" if error == "You have already applied." else "danger")
		return redirect(url_for("student.scholarships"))

	subdir = f"user_{current_user.user_id}"
	income_path = save_uploaded(income_file, subdir)
	govt_id_path = save_uploaded(govt_id_file, subdir)

	app = Application(
		student_id=current_user.user_id,
		scholarship_id=scholarship_id,
		cgpa_value=cgpa_value,
		income_proof_path=income_path,
		govt_id_path=govt_id_path,
	)
	db.session.add(app)
	try:
		db.session.commit()
	except IntegrityError:
		# Double submit: the unique constraint caught a duplicate application
		db.session.rollback()
		for rel in (income_path, govt_id_path):
			try:
				os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], rel))
			except OSError:
				pass
		flash("You have already applied.", "warning")
		return redirect(url_for("student.scholarships"))
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
	name = request.form.get("name", "").strip()
	try:
		cgpa = parse_float(request.form.get("cgpa"), "CGPA", 0, 10)
		income = parse_float(request.form.get("family_income"), "Family income", 0)
	except ValueError as e:
		flash(str(e), "danger")
		return redirect(url_for("student.profile"))
	if name:
		current_user.name = name
	current_user.department = request.form.get("department", "").strip() or None
	if cgpa is not None:
		current_user.cgpa = cgpa
	if income is not None:
		current_user.family_income = income
	db.session.commit()
	flash("Profile updated", "success")
	return redirect(url_for("student.profile"))
