from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import db
from .models import User
from .utils import hash_password, check_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
	return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
	email = request.form.get("email", "").strip().lower()
	password = request.form.get("password", "")
	user = db.session.query(User).filter_by(email=email).first()
	if not user or not check_password(password, user.password_hash):
		flash("Invalid credentials", "danger")
		return redirect(url_for("auth.login"))
	login_user(user)
	return redirect(url_for("index"))


@auth_bp.get("/register")
def register():
	return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
	name = request.form.get("name", "").strip()
	email = request.form.get("email", "").strip().lower()
	password = request.form.get("password", "")
	department = request.form.get("department")
	role = request.form.get("role") or "student"
	if db.session.query(User).filter_by(email=email).first():
		flash("Email already registered", "warning")
		return redirect(url_for("auth.register"))
	user = User(
		name=name,
		email=email,
		password_hash=hash_password(password),
		role=role,
		department=department,
	)
	db.session.add(user)
	db.session.commit()
	flash("Registration successful. You can login now.", "success")
	return redirect(url_for("auth.login"))


@auth_bp.get("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("auth.login"))



