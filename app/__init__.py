from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path
import os

# Global extensions
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
	# Use absolute path for instance folders
	base_dir = Path(__file__).resolve().parent.parent
	instance_path = base_dir / 'instance'
	
	app = Flask(__name__, instance_path=str(instance_path), instance_relative_config=True)

	# Default configuration
	app.config.from_mapping(
		SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
		SQLALCHEMY_DATABASE_URI=os.environ.get(
			"DATABASE_URL",
			# Default to SQLite file in instance folder
			f"sqlite:///{Path(app.instance_path) / 'scholarships.db'}",
		),
		SQLALCHEMY_TRACK_MODIFICATIONS=False,
		MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10 MB uploads
		UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"),
	)

	# Ensure instance folders exist
	Path(app.instance_path).mkdir(parents=True, exist_ok=True)
	Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

	# Init extensions
	login_manager.init_app(app)
	login_manager.login_view = "auth.login"
	db.init_app(app)
	migrate.init_app(app, db)

	# Register blueprints
	from .auth import auth_bp
	from .routes_admin import admin_bp
	from .routes_student import student_bp
	from .routes_api import api_bp

	app.register_blueprint(auth_bp)
	app.register_blueprint(admin_bp, url_prefix="/admin")
	app.register_blueprint(student_bp, url_prefix="/student")
	app.register_blueprint(api_bp, url_prefix="/api")

	# Static serving for uploaded files
	from flask import send_from_directory

	@app.get("/uploads/<path:path>")
	def uploads_file(path: str):
		return send_from_directory(app.config["UPLOAD_FOLDER"], path, as_attachment=False)

	# Jinja filters
	from .utils import upload_url as _upload_url, is_pdf as _is_pdf
	app.jinja_env.filters["upload_url"] = _upload_url
	app.jinja_env.filters["is_pdf"] = _is_pdf

	# Index route
	@app.get("/")
	def index():
		from flask_login import current_user
		from flask import redirect, url_for, render_template
		if current_user.is_authenticated:
			if current_user.role == "admin":
				return redirect(url_for("admin.dashboard"))
			return redirect(url_for("student.dashboard"))
		return render_template("index.html")

	return app
