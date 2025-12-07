import os
import bcrypt
from functools import wraps
from flask import current_app, abort
from flask_login import current_user
from werkzeug.utils import secure_filename

ALLOWED_DOC_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


def hash_password(plain: str) -> str:
	return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(plain: str, hashed: str) -> bool:
	try:
		return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
	except Exception:
		return False


def role_required(*roles: str):
	def decorator(view_func):
		@wraps(view_func)
		def wrapper(*args, **kwargs):
			if not current_user.is_authenticated:
				abort(401)
			if current_user.role not in roles:
				abort(403)
			return view_func(*args, **kwargs)
		return wrapper
	return decorator


def save_uploaded(file_storage, subdir: str) -> str:
	if not file_storage or not getattr(file_storage, "filename", ""):
		return ""
	filename = secure_filename(file_storage.filename)
	ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
	if ext not in ALLOWED_DOC_EXTENSIONS:
		raise ValueError("Invalid file type. Allowed: pdf, jpg, jpeg, png")
	upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subdir)
	os.makedirs(upload_dir, exist_ok=True)
	path = os.path.join(upload_dir, filename)
	file_storage.save(path)
	# store path relative to UPLOAD_FOLDER for portable URL building
	rel = os.path.relpath(path, start=current_app.config["UPLOAD_FOLDER"]).replace("\\", "/")
	return rel


def upload_url(stored_path: str) -> str:
	if not stored_path:
		return ""
	stored_path = stored_path.replace("\\", "/")
	# If absolute, make it relative to UPLOAD_FOLDER when possible
	if os.path.isabs(stored_path):
		try:
			rel = os.path.relpath(stored_path, start=current_app.config["UPLOAD_FOLDER"]).replace("\\", "/")
		except Exception:
			rel = os.path.basename(stored_path)
	else:
		rel = stored_path
	return f"/uploads/{rel}"


def is_pdf(stored_path: str) -> bool:
	if not stored_path:
		return False
	return str(stored_path).lower().endswith(".pdf")
