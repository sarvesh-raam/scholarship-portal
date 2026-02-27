# 🎓 Scholarship & Financial Aid Portal

[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen.svg)](https://scholarshipportal.pythonanywhere.com)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com/)

A modern, full-stack **Scholarship Management System** designed to streamline the application process for students and management for administrators.

---

## 🌐 Live Demo
You can access the live portal here:  
👉 **[scholarshipportal.pythonanywhere.com](https://scholarshipportal.pythonanywhere.com)**

### 🔑 Test Credentials
| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `admin123` |
| **Student** | `student@example.com` | `student123` |

---

## ✨ Features
- **🔐 Secure Authentication**: Role-based access control with hashed passwords (Bcrypt).
- **📊 Admin Dashboard**: Manage scholarships, review applications, and track budgets.
- **🎓 Student Portal**: Search for eligibility, apply for schemes, and view status.
- **💰 Financial Reporting**: Dynamic breakdown of allocated vs. remaining funds.
- **📱 Responsive UI**: Clean, modern design that works on all devices.

---

## 🛠️ Tech Stack
- **Backend**: Python, Flask
- **Database**: SQLite (Production-ready via SQLAlchemy)
- **Frontend**: Vanilla CSS3, HTML5, Jinja2 Templates
- **Deployment**: PythonAnywhere

---

## 🤝 Contributors

| Contributor | Focus |
| :---: | :--- |
| <img src="https://github.com/sarvesh-raam.png?size=100" width="100px;" alt="Sarvesh Raam"/><br />**[Sarvesh Raam](https://github.com/sarvesh-raam)** | Project Lead, Backend Architecture, Database Design, Cloud Deployment |
| <img src="https://github.com/arunkumarc05.png?size=100" width="100px;" alt="Arunkumar C"/><br />**[Arunkumar C](https://github.com/arunkumarc05)** | UI Refinement, Frontend Logic, Documentation & Testing |

---

## 🚀 Local Setup
```bash
git clone https://github.com/sarvesh-raam/scholarship-portal.git
cd scholarship-portal
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py
```
<<<<<<< HEAD
=======

Login with:
- Admin: `admin@example.com` / `admin123`
- Student: `student@example.com` / `student123`

## SQLite vs MySQL
Default is SQLite (file in `instance/scholarships.db`). To use MySQL:
- Set env var `DATABASE_URL` like: `mysql://user:password@localhost:3306/scholarships`
- Ensure MySQL is running and database exists.

## File Uploads
- Uploads are stored under `instance/uploads/`
- Allowed types: pdf, jpg, jpeg, png
- Max size: 10 MB (configurable via `MAX_CONTENT_LENGTH`)

## Database Schema (DDL)
```sql
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL,
  department VARCHAR(80),
  cgpa FLOAT,
  family_income FLOAT
);

CREATE TABLE scholarships (
  scholarship_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(150) NOT NULL,
  category VARCHAR(50) NOT NULL,
  eligibility TEXT NOT NULL,
  amount FLOAT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  min_cgpa FLOAT,
  income_limit FLOAT
);

CREATE TABLE applications (
  application_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  student_id INTEGER NOT NULL,
  scholarship_id INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  submitted_date DATETIME,
  reviewed_by INTEGER,
  remarks TEXT,
  income_proof_path VARCHAR(255),
  govt_id_path VARCHAR(255),
  cgpa_value FLOAT,
  CONSTRAINT fk_app_student FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_app_sch FOREIGN KEY (scholarship_id) REFERENCES scholarships(scholarship_id) ON DELETE CASCADE
);

CREATE TABLE finance (
  fund_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  year INTEGER NOT NULL UNIQUE,
  budget_amount FLOAT NOT NULL DEFAULT 0,
  allocated_amount FLOAT NOT NULL DEFAULT 0,
  balance_amount FLOAT NOT NULL DEFAULT 0
);
```

## Screenshots
- Add screenshots of Admin Dashboard, Scholarships, Applications, Finance, Student pages.

## Reports & Analytics
- Pie: distribution by `scholarships.category`
- Bar: applications per `users.department`
- Fund usage: shown in dashboard and `/api/fund-report/year`

## Security Notes
- Passwords are hashed with bcrypt
- Role checks guard admin/student routes
- Inputs validated server-side; duplicate applications prevented
- File uploads sanitized via `secure_filename`

## Project Structure
```
app/
  __init__.py
  models.py
  auth.py
  routes_student.py
  routes_admin.py
  routes_api.py
  templates/
    layout.html
    index.html
    auth/
      login.html
      register.html
    student/
      dashboard.html
      scholarships.html
      profile.html
    admin/
      dashboard.html
      scholarships.html
      applications.html
      finance.html
instance/ (created on first run)
uploads/ (inside instance)
requirements.txt
run.py
seed.py
```

## Deliverables
- Running app with above features
- UI screenshots (to be captured after running locally)
- Working source code (this repo)
- Database schema (DDL above)
- Short report: abstract, modules, and conclusion (can be derived from README sections)

- ## Team
- **Sarvesh Raam** (@sarvesh-raam)
- **Arunkumar C** (@arunkumarc05)




>>>>>>> 6803d83b65e925e0de9038836d1daee411443a3e
