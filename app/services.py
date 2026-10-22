"""Business rules shared by the HTML routes and the JSON API."""
from datetime import date
from typing import Optional
from . import db
from .models import Application, Finance, Scholarship, User

DECISION_STATUSES = {"approved", "rejected"}


def eligibility_error(student: User, sch: Scholarship, cgpa_value: Optional[float]) -> Optional[str]:
	"""Return a user-facing reason the student cannot apply, or None if they can."""
	today = date.today()
	if not (sch.start_date <= today <= sch.end_date):
		return "This scholarship is not open for applications."
	if sch.min_cgpa is not None:
		if cgpa_value is None:
			return "CGPA is required for this scholarship."
		if cgpa_value < sch.min_cgpa:
			return "CGPA below required minimum."
	if sch.income_limit is not None:
		if student.family_income is None:
			return "Add your family income to your profile before applying for this scholarship."
		if float(student.family_income) > float(sch.income_limit):
			return "Family income exceeds limit."
	already = db.session.query(Application).filter_by(student_id=student.user_id, scholarship_id=sch.scholarship_id).first()
	if already:
		return "You have already applied."
	return None


def decide_application(app: Application, status: str, remarks: Optional[str], reviewer: User) -> Optional[str]:
	"""Approve or reject a pending application, updating the current year's fund.

	Returns an error message, or None on success. Only pending applications can be decided,
	so an approval can never be counted against the budget twice.
	"""
	if status not in DECISION_STATUSES:
		return "Invalid status."
	if app.status != "pending":
		return f"Application #{app.application_id} has already been {app.status}."
	if status == "approved":
		fund = db.session.query(Finance).filter_by(year=date.today().year).first()
		if not fund:
			return f"No budget has been set for {date.today().year}. Set one on the Finance page first."
		amount = float(app.scholarship.amount)
		if not fund.can_allocate(amount):
			return f"Insufficient balance: ₹{fund.balance_amount:,.0f} left, ₹{amount:,.0f} needed."
		fund.allocated_amount = float(fund.allocated_amount or 0) + amount
		fund.recalc()
	app.status = status
	app.remarks = (remarks or "").strip() or None
	app.reviewed_by = reviewer.user_id
	db.session.commit()
	return None
