"""Create the database tables and demo data.

Credentials can be overridden with environment variables so a public deployment
does not use the well-known demo passwords:
    ADMIN_EMAIL, ADMIN_PASSWORD, SEED_DEMO_STUDENT=0
"""
import os
from datetime import date, timedelta
from app import create_app, db
from app.models import User, Scholarship, Finance
from app.utils import hash_password

app = create_app()

admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com").strip().lower()
admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
seed_student = os.environ.get("SEED_DEMO_STUDENT", "1") == "1"

with app.app_context():
	db.create_all()
	if not db.session.query(User).filter_by(email=admin_email).first():
		admin = User(name="Admin", email=admin_email, password_hash=hash_password(admin_password), role="admin")
		db.session.add(admin)
		print(f"Created admin: {admin_email}")
		if "ADMIN_PASSWORD" not in os.environ:
			print("WARNING: using the default demo password 'admin123'. Set ADMIN_PASSWORD for a public deployment.")
	if seed_student and not db.session.query(User).filter_by(email="student@example.com").first():
		student = User(name="Student One", email="student@example.com", password_hash=hash_password("student123"), role="student", department="CSE", cgpa=8.2, family_income=250000)
		db.session.add(student)
		print("Created student: student@example.com / student123")
	if not db.session.query(Scholarship).count():
		today = date.today()
		db.session.add_all([
			Scholarship(name="Merit Excellence", category="merit", eligibility="CGPA >= 8.0", amount=20000, start_date=today, end_date=today + timedelta(days=60), min_cgpa=8.0),
			Scholarship(name="Need Based Support", category="financial", eligibility="Income <= 3L", amount=30000, start_date=today, end_date=today + timedelta(days=45), income_limit=300000),
		])
		print("Seeded scholarships")
	if not db.session.query(Finance).filter_by(year=date.today().year).first():
		fund = Finance(year=date.today().year, budget_amount=500000, allocated_amount=0)
		fund.recalc()
		db.session.add(fund)
		print("Seeded finance for current year")
	db.session.commit()
	print("Done.")
