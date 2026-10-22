from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
import os
import secrets

# Global extensions
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def _load_secret_key(instance_path: Path) -> str:
	# Prefer the environment; otherwise persist a random key in the instance folder
	# so sessions survive restarts and the key is never hard-coded in the repo.
	key = os.environ.get("SECRET_KEY")
	if key:
		return key
	key_file = instance_path / "secret_key"
	if key_file.exists():
		return key_file.read_text().strip()
	key = secrets.token_hex(32)
	key_file.write_text(key)
	return key


def create_app(test_config: dict | None = None):
	# Use absolute path for instance folders
	base_dir = Path(__file__).resolve().parent.parent
	instance_path = base_dir / 'instance'
	instance_path.mkdir(parents=True, exist_ok=True)

	app = Flask(__name__, instance_path=str(instance_path), instance_relative_config=True)

	database_url = os.environ.get("DATABASE_URL", f"sqlite:///{instance_path / 'scholarships.db'}")
	# Some hosts still hand out the legacy "postgres://" scheme, which SQLAlchemy 2 rejects
	if database_url.startswith("postgres://"):
		database_url = database_url.replace("postgres://", "postgresql://", 1)

	# Default configuration
	app.config.from_mapping(
		SECRET_KEY=_load_secret_key(instance_path),
		SQLALCHEMY_DATABASE_URI=database_url,
		SQLALCHEMY_TRACK_MODIFICATIONS=False,
		SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
		MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB uploads
		UPLOAD_FOLDER=str(instance_path / "uploads"),
		SESSION_COOKIE_HTTPONLY=True,
		SESSION_COOKIE_SAMESITE="Lax",
		SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0") == "1",
		REMEMBER_COOKIE_HTTPONLY=True,
	)
	if test_config:
		app.config.update(test_config)

	# Ensure upload folder exists
	Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

	# Init extensions
	login_manager.init_app(app)
	login_manager.login_view = "auth.login"
	login_manager.login_message_category = "warning"
	# API clients get a JSON 401 instead of a redirect to the HTML login page
	login_manager.blueprint_login_views = {"api": None}
	db.init_app(app)
	migrate.init_app(app, db)
	csrf.init_app(app)

	# Register blueprints
	from .auth import auth_bp
	from .routes_admin import admin_bp
	from .routes_student import student_bp
	from .routes_api import api_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(admin_bp, url_prefix="/admin")
	app.register_blueprint(student_bp, url_prefix="/student")
	# The JSON API is protected by requiring a JSON content type instead of a CSRF token
	csrf.exempt(api_bp)
	app.register_blueprint(api_bp, url_prefix="/api")

	from flask import send_from_directory, abort, render_template, redirect, url_for
	from flask_login import current_user, login_required

	# Uploaded documents are private: only admins and the student who uploaded them may view them
	@app.get("/uploads/<path:path>")
	@login_required
	def uploads_file(path: str):
		if current_user.role != "admin" and not path.startswith(f"user_{current_user.user_id}/"):
			abort(403)
		return send_from_directory(app.config["UPLOAD_FOLDER"], path, as_attachment=False)

	# Jinja filters
	from .utils import upload_url as _upload_url, is_pdf as _is_pdf
	app.jinja_env.filters["upload_url"] = _upload_url
	app.jinja_env.filters["is_pdf"] = _is_pdf

	# Index route
	@app.get("/")
	def index():
		if current_user.is_authenticated:
			if current_user.role == "admin":
				return redirect(url_for("admin.dashboard"))
			return redirect(url_for("student.dashboard"))
		return render_template("index.html")

	# Friendly error pages
	from flask_wtf.csrf import CSRFError

	error_messages = {
		400: "The request could not be processed.",
		401: "Please log in to continue.",
		403: "You do not have permission to view this page.",
		404: "The page you are looking for does not exist.",
		413: "The uploaded file is too large (maximum 10 MB).",
		500: "Something went wrong on our side. Please try again.",
	}

	def render_error(code: int, message: str | None = None):
		return render_template("error.html", code=code, message=message or error_messages.get(code, "")), code

	for code in error_messages:
		app.register_error_handler(code, lambda e, code=code: render_error(code))

	@app.errorhandler(CSRFError)
	def handle_csrf_error(e):
		return render_error(400, "Your session expired. Please go back, refresh the page and try again.")

	# Make sure the schema exists on a fresh deployment, even before seed.py runs
	from . import models  # noqa: F401
	with app.app_context():
		db.create_all()

	return app
