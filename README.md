# College Scholarships & Financial Aid

A full-stack Flask (Python) + SQLite/MySQL app for managing scholarship schemes, student applications, and finance allocation. Clean, responsive UI with Bootstrap and charts via Chart.js.

## Features
- Admin and Student roles (role-based access)
- Admin dashboard: metrics, charts, finance summary
- Scholarship CRUD (name, category, eligibility, amount, start/end, thresholds)
- Student portal: profile, browse/apply with uploads, status/history
- Review workflow: approve/reject, remarks; finance auto-updates on approval
- REST API: `/api/login`, `/api/scholarships`, `/api/apply`, `/api/approve`, `/api/fund-report/year`
- Secure auth (bcrypt hashing), input validation, duplicate prevention, file uploads

## Quickstart (Windows PowerShell)
```powershell
# 1) Create and activate venv
python -m venv .venv
.\.venv\Scripts\activate

# 2) Install deps
pip install -r requirements.txt

# 3) Initialize DB and seed sample data
python .\seed.py

# 4) Run
python .\run.py
# open http://127.0.0.1:5000
```

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



