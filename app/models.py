from datetime import datetime
from typing import Optional
from . import db, login_manager
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Text, Float, CheckConstraint


class User(db.Model, UserMixin):
	__tablename__ = "users"

	user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(120), nullable=False)
	email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
	department: Mapped[Optional[str]] = mapped_column(String(80))
	cgpa: Mapped[Optional[float]] = mapped_column(Float)
	family_income: Mapped[Optional[float]] = mapped_column(Float)

	applications: Mapped[list["Application"]] = relationship(
		"Application",
		back_populates="student",
		cascade="all, delete-orphan",
		foreign_keys="Application.student_id",
	)

	def get_id(self) -> str:  # Flask-Login expects string id
		return str(self.user_id)


@login_manager.user_loader
def load_user(user_id: str) -> Optional["User"]:
	return db.session.get(User, int(user_id))


class Scholarship(db.Model):
	__tablename__ = "scholarships"

	scholarship_id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(150), nullable=False)
	category: Mapped[str] = mapped_column(String(50), nullable=False)
	eligibility: Mapped[str] = mapped_column(Text, nullable=False)
	amount: Mapped[float] = mapped_column(Float, nullable=False)
	start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
	end_date: Mapped[datetime] = mapped_column(Date, nullable=False)
	min_cgpa: Mapped[Optional[float]] = mapped_column(Float)
	income_limit: Mapped[Optional[float]] = mapped_column(Float)

	applications: Mapped[list["Application"]] = relationship(
		back_populates="scholarship", cascade="all, delete-orphan"
	)


class Application(db.Model):
	__tablename__ = "applications"

	application_id: Mapped[int] = mapped_column(Integer, primary_key=True)
	student_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
	scholarship_id: Mapped[int] = mapped_column(
		ForeignKey("scholarships.scholarship_id", ondelete="CASCADE"), nullable=False
	)
	status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
	submitted_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.user_id"))
	remarks: Mapped[Optional[str]] = mapped_column(Text)
	income_proof_path: Mapped[Optional[str]] = mapped_column(String(255))
	govt_id_path: Mapped[Optional[str]] = mapped_column(String(255))
	cgpa_value: Mapped[Optional[float]] = mapped_column(Float)

	student: Mapped[User] = relationship("User", foreign_keys=[student_id], back_populates="applications")
	scholarship: Mapped[Scholarship] = relationship("Scholarship", back_populates="applications")
	reviewer: Mapped[Optional[User]] = relationship("User", foreign_keys=[reviewed_by])

	__table_args__ = (
		CheckConstraint("cgpa_value IS NULL OR (cgpa_value >= 0 AND cgpa_value <= 10)", name="ck_cgpa_range"),
	)


class Finance(db.Model):
	__tablename__ = "finance"

	fund_id: Mapped[int] = mapped_column(Integer, primary_key=True)
	year: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
	budget_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	allocated_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
	balance_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)

	def recalc(self) -> None:
		self.balance_amount = max(0.0, float(self.budget_amount) - float(self.allocated_amount))
