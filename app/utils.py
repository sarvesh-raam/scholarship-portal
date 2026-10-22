import os
import uuid
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


def parse_float(value, field: str, min_value: float | None = None, max_value: float | None = None) -> float | None:
	"""Parse an optional numeric form/JSON value; raise ValueError with a user-facing message."""
	if value is None or (isinstance(value, str) and not value.strip()):
		return None
	try:
		number = float(value)
	except (TypeError, ValueError):
		raise ValueError(f"{field} must be a number.")
	if number != number or number in (float("inf"), float("-inf")):
		raise ValueError(f"{field} must be a number.")
	if min_value is not None and number < min_value:
		raise ValueError(f"{field} must be at least {min_value:g}.")
	if max_value is not None and number > max_value:
		raise ValueError(f"{field} must be at most {max_value:g}.")
	return number


def parse_int(value, field: str) -> int:
	try:
		return int(value)
	except (TypeError, ValueError):
		raise ValueError(f"{field} must be a whole number.")


def has_upload(file_storage) -> bool:
	return bool(file_storage and getattr(file_storage, "filename", ""))


def validate_upload(file_storage) -> str:
	"""Return the lowercase extension of an upload, or raise ValueError if it is not allowed."""
	filename = secure_filename(file_storage.filename)
	ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
	if ext not in ALLOWED_DOC_EXTENSIONS:
		raise ValueError("Invalid file type. Allowed: pdf, jpg, jpeg, png")
	return ext


def save_uploaded(file_storage, subdir: str) -> str:
	if not has_upload(file_storage):
		return ""
	ext = validate_upload(file_storage)
	upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subdir)
	os.makedirs(upload_dir, exist_ok=True)
	# Random name so two uploads with the same original filename never overwrite each other
	path = os.path.join(upload_dir, f"{uuid.uuid4().hex}.{ext}")
	file_storage.save(path)
	# store path relative to UPLOAD_FOLDER for portable URL building
	rel = os.path.relpath(path, start=current_app.config["UPLOAD_FOLDER"]).replace("\\", "/")
	return rel


def upload_url(stored_path: str) -> str:
	if not stored_path:
		return ""
	stored_path = stored_path.replace("\\", "/")
	# Legacy rows stored absolute paths from another machine (e.g. E:/DBMS/instance/uploads/...)
	if "/uploads/" in stored_path:
		rel = stored_path.rsplit("/uploads/", 1)[1]
	elif os.path.isabs(stored_path):
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
