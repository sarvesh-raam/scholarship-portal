from urllib.parse import urlsplit
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email, EmailNotValidError
from . import db
from .models import User
from .utils import hash_password, check_password

auth_bp = Blueprint("auth", __name__)

MIN_PASSWORD_LENGTH = 8


def _safe_next(target: str | None) -> str | None:
	# Only allow relative redirects back into this site (prevents open redirects)
	if not target:
		return None
	parts = urlsplit(target)
	if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
		return None
	return target


@auth_bp.get("/login")
def login():
	if current_user.is_authenticated:
		return redirect(url_for("index"))
	return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
	email = request.form.get("email", "").strip().lower()
	password = request.form.get("password", "")
	user = db.session.query(User).filter_by(email=email).first()
	if not user or not check_password(password, user.password_hash):
		flash("Invalid credentials", "danger")
		return redirect(url_for("auth.login", next=request.args.get("next")))
	login_user(user)
	return redirect(_safe_next(request.args.get("next")) or url_for("index"))


@auth_bp.get("/register")
def register():
	if current_user.is_authenticated:
		return redirect(url_for("index"))
	return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
	name = request.form.get("name", "").strip()
	email = request.form.get("email", "").strip().lower()
	password = request.form.get("password", "")
	department = request.form.get("department", "").strip() or None
	# Public registration always creates students; admins are created with seed.py
	errors = []
	if not name:
		errors.append("Name is required.")
	try:
		email = validate_email(email, check_deliverability=False).normalized.lower()
	except EmailNotValidError:
		errors.append("Enter a valid email address.")
	if len(password) < MIN_PASSWORD_LENGTH:
		errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
	if errors:
		for err in errors:
			flash(err, "danger")
		return redirect(url_for("auth.register"))
	if db.session.query(User).filter_by(email=email).first():
		flash("Email already registered", "warning")
		return redirect(url_for("auth.register"))
	user = User(
		name=name,
		email=email,
		password_hash=hash_password(password),
		role="student",
		department=department,
	)
	db.session.add(user)
	db.session.commit()
	flash("Registration successful. You can login now.", "success")
	return redirect(url_for("auth.login"))


@auth_bp.post("/logout")
@login_required
def logout():
	logout_user()
	flash("You have been logged out.", "success")
	return redirect(url_for("auth.login"))
