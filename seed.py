from datetime import date, timedelta
from app import create_app, db
from app.models import User, Scholarship, Finance
from app.utils import hash_password

app = create_app()

with app.app_context():
	db.create_all()
	if not db.session.query(User).filter_by(email="admin@example.com").first():
		admin = User(name="Admin", email="admin@example.com", password_hash=hash_password("admin123"), role="admin")
		db.session.add(admin)
		print("Created admin: admin@example.com / admin123")
	if not db.session.query(User).filter_by(email="student@example.com").first():
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
		db.session.add(Finance(year=date.today().year, budget_amount=500000))
		print("Seeded finance for current year")
	db.session.commit()
	print("Done.")



