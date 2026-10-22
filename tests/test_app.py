import io
from datetime import date, timedelta

import pytest

from app import create_app, db
from app.models import User, Scholarship, Application, Finance
from app.utils import hash_password


@pytest.fixture()
def app(tmp_path):
	app = create_app({
		"TESTING": True,
		"WTF_CSRF_ENABLED": False,
		"SECRET_KEY": "test",
		"SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
		"UPLOAD_FOLDER": str(tmp_path / "uploads"),
	})
	with app.app_context():
		db.create_all()
		today = date.today()
		db.session.add_all([
			User(name="Admin", email="admin@example.com", password_hash=hash_password("admin123"), role="admin"),
			User(name="Stu", email="stu@example.com", password_hash=hash_password("student123"), role="student", department="CSE", cgpa=8.5, family_income=200000),
			User(name="Other", email="other@example.com", password_hash=hash_password("student123"), role="student", family_income=200000),
			Scholarship(name="Merit", category="merit", eligibility="CGPA>=8", amount=20000, start_date=today, end_date=today + timedelta(days=30), min_cgpa=8.0),
			Scholarship(name="Need", category="financial", eligibility="Income<=3L", amount=30000, start_date=today, end_date=today + timedelta(days=30), income_limit=300000),
			Scholarship(name="Expired", category="sports", eligibility="-", amount=5000, start_date=today - timedelta(days=30), end_date=today - timedelta(days=1)),
			Finance(year=today.year, budget_amount=40000, allocated_amount=0, balance_amount=40000),
		])
		db.session.commit()
	yield app


@pytest.fixture()
def client(app):
	return app.test_client()


def login(client, email, password):
	return client.post("/login", data={"email": email, "password": password})


def files():
	return {
		"cgpa": "8.5",
		"income_proof": (io.BytesIO(b"%PDF-1.4"), "proof.pdf"),
		"govt_id": (io.BytesIO(b"\x89PNG"), "id.png"),
	}


def apply(client, sch_id, **overrides):
	data = files()
	data.update(overrides)
	return client.post(f"/student/apply/{sch_id}", data=data, content_type="multipart/form-data")


def test_register_cannot_create_admin(client, app):
	client.post("/register", data={"name": "Eve", "email": "eve@example.com", "password": "password123", "role": "admin"})
	with app.app_context():
		assert db.session.query(User).filter_by(email="eve@example.com").one().role == "student"


def test_register_rejects_short_password(client, app):
	client.post("/register", data={"name": "Eve", "email": "eve@example.com", "password": "x"})
	with app.app_context():
		assert db.session.query(User).filter_by(email="eve@example.com").first() is None


def test_login_next_redirect_is_safe(client):
	r = client.post("/login?next=https://evil.example/", data={"email": "stu@example.com", "password": "student123"})
	assert r.status_code == 302 and "evil.example" not in r.headers["Location"]


def test_bad_numbers_do_not_crash(client):
	login(client, "stu@example.com", "student123")
	assert client.post("/student/profile", data={"name": "Stu", "cgpa": "abc"}).status_code == 302
	assert client.post("/student/profile", data={"name": "Stu", "cgpa": "11"}).status_code == 302
	assert apply(client, 1, cgpa="12").status_code == 302
	client.post("/logout")
	login(client, "admin@example.com", "admin123")
	assert client.post("/admin/finance", data={}).status_code == 302
	assert client.post("/admin/scholarships", data={"name": "x", "amount": "nope"}).status_code == 302


def test_cannot_apply_twice_or_to_expired(client, app):
	login(client, "stu@example.com", "student123")
	assert apply(client, 1).status_code == 302
	apply(client, 1)
	apply(client, 3)
	with app.app_context():
		assert db.session.query(Application).filter_by(scholarship_id=1).count() == 1
		assert db.session.query(Application).filter_by(scholarship_id=3).count() == 0


def test_income_limit_requires_profile_income(client, app):
	with app.app_context():
		db.session.get(User, 3).family_income = None
		db.session.commit()
	login(client, "other@example.com", "student123")
	apply(client, 2)
	with app.app_context():
		assert db.session.query(Application).count() == 0


def test_approval_counts_budget_once_and_respects_balance(client, app):
	login(client, "stu@example.com", "student123")
	apply(client, 1)
	apply(client, 2)
	client.post("/logout")
	login(client, "admin@example.com", "admin123")
	client.post("/admin/applications/1/decision", data={"status": "approved"})
	# Re-submitting a decision must not count the money again or flip the status
	client.post("/admin/applications/1/decision", data={"status": "approved"})
	client.post("/admin/applications/1/decision", data={"status": "rejected"})
	# 20k left in the budget, the 30k scholarship cannot be approved
	client.post("/admin/applications/2/decision", data={"status": "approved"})
	with app.app_context():
		fund = db.session.query(Finance).one()
		assert fund.allocated_amount == 20000 and fund.balance_amount == 20000
		assert db.session.get(Application, 1).status == "approved"
		assert db.session.get(Application, 2).status == "pending"


def test_uploads_are_private(client, app):
	login(client, "stu@example.com", "student123")
	apply(client, 1)
	with app.app_context():
		path = db.session.get(Application, 1).income_proof_path
	assert client.get(f"/uploads/{path}").status_code == 200
	client.post("/logout")
	assert client.get(f"/uploads/{path}").status_code == 302  # anonymous -> login
	login(client, "other@example.com", "student123")
	assert client.get(f"/uploads/{path}").status_code == 403
	client.post("/logout")
	login(client, "admin@example.com", "admin123")
	assert client.get(f"/uploads/{path}").status_code == 200


def test_all_pages_render(client):
	assert client.get("/").status_code == 200
	assert client.get("/login").status_code == 200
	assert client.get("/register").status_code == 200
	assert client.get("/does-not-exist").status_code == 404
	login(client, "stu@example.com", "student123")
	apply(client, 1)
	for url in ["/student/dashboard", "/student/scholarships", "/student/profile"]:
		assert client.get(url).status_code == 200, url
	assert client.get("/admin/dashboard").status_code == 403
	client.post("/logout")
	login(client, "admin@example.com", "admin123")
	for url in ["/admin/dashboard", "/admin/students", "/admin/scholarships", "/admin/applications", "/admin/applications?status=pending", "/admin/finance"]:
		assert client.get(url).status_code == 200, url


def test_dashboard_handles_student_without_department(client, app):
	login(client, "other@example.com", "student123")
	apply(client, 1)
	client.post("/logout")
	login(client, "admin@example.com", "admin123")
	assert client.get("/admin/dashboard").status_code == 200


def test_api_flow(client):
	assert client.get("/api/scholarships").status_code == 401
	assert client.post("/api/login", data="email=x").status_code == 415
	r = client.post("/api/login", json={"email": "stu@example.com", "password": "student123"})
	assert r.status_code == 200 and r.json["ok"]
	assert client.get("/api/scholarships").status_code == 200
	assert client.post("/api/apply", json={}).status_code == 400
	assert client.post("/api/apply", json={"scholarship_id": 999}).status_code == 404
	assert client.post("/api/apply", json={"scholarship_id": 1, "cgpa": 9}).status_code == 201
	assert client.post("/api/apply", json={"scholarship_id": 1, "cgpa": 9}).status_code == 409
	assert client.post("/api/approve", json={"application_id": 1, "status": "approved"}).status_code == 403
	assert client.get("/api/fund-report/year").status_code == 403


def test_csrf_enforced_on_forms(app):
	app.config["WTF_CSRF_ENABLED"] = True
	client = app.test_client()
	r = client.post("/register", data={"name": "Eve", "email": "eve@example.com", "password": "password123"})
	assert r.status_code == 400
