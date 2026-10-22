# Scholarship Management and Financial Portal

From eligibility screening to automated budget tracking, this platform serves as a unified gateway for student financial aid management and oversight.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=flat-square&logo=render&logoColor=white)](https://scholarshipportal.pythonanywhere.com/)
[![Backend](https://img.shields.io/badge/Backend-Flask%20%2B%20SQLite-3776AB?style=flat-square&logo=python&logoColor=white)](#)

---

## Executive Summary
This portal is designed to provide a single source of truth for student financial aid, applications, and payouts. It offers decision-ready insights into scholarship impact and features a zero-friction deployment optimized for production environments. Designed with scalability and modular architecture in mind.

## Deployment Proof
Deployed and running in production on PythonAnywhere: [View Live Portal](https://scholarshipportal.pythonanywhere.com/)

## Architecture and System Design
The application follows a traditional Model-View-Controller (MVC) architectural pattern, clearly separating backend logic from frontend presentation.

- **Frontend**: HTML5, CSS3, and Jinja2 templating for dynamic rendering.
- **Backend Framework**: Python Flask handling routing, middleware, and business logic.
- **Database**: SQLite (Development/Production) via SQLAlchemy ORM.
- **Authentication**: Bcrypt for secure password hashing and Role-Based Access Control (RBAC).

## API Design
- REST endpoints for data processing
- Structured request-response pipeline
- Error handling and validation

## System Design & Scale
- Engineered to handle concurrent student application flows and automated eligibility checking.
- Designed to scale to thousands of users (students and administrators) with isolated session management.
- Dynamic budget recalibration happens at scale without degrading read-response times.

## Core Capabilities
- **Admin Command Center**: Complete budget oversight, scheme creation, and application review processes.
- **Student Gateway**: Real-time eligibility search, CGPA verification, and application status tracking.
- **Finance Engine**: Automated budget recalculation and live balance tracking across scholarship schemes.
- **Smart Eligibility Filter**: Automatic filtering based on student category, income limit checks, and minimum CGPA validation.

## Technical Structure
```text
scholarship-portal/
├── app/
│   ├── static/                  # Images
│   ├── templates/               # Jinja2 HTML views (+ _macros.html, error.html)
│   ├── __init__.py              # App factory, security config, error pages
│   ├── models.py                # Database schema (ORM)
│   ├── services.py              # Eligibility + approval/budget rules (shared by web & API)
│   ├── auth.py                  # Login / registration
│   ├── routes_admin.py          # Admin pages
│   ├── routes_student.py        # Student pages
│   └── routes_api.py            # JSON API
├── tests/                       # pytest suite
├── instance/                    # Local database, uploads, secret key (not committed)
├── wsgi.py                      # WSGI entry point (PythonAnywhere / gunicorn)
├── seed.py                      # Creates tables + demo data
└── run.py                       # Local development server
```

## Quickstart Guide

### 1. Clone
```bash
git clone https://github.com/sarvesh-raam/scholarship-portal.git
cd scholarship-portal
```

### 2. Create an environment
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
On Windows you can simply run `start.bat`, which does all of the above plus steps 3–4.

### 3. Initialize and run
```bash
python seed.py
python run.py                    # http://localhost:5000
```
Demo accounts: `admin@example.com / admin123` and `student@example.com / student123`.
Public registration always creates **student** accounts; admins are created by `seed.py`.

### 4. Run the tests
```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Signs sessions and CSRF tokens | random key generated in `instance/secret_key` |
| `DATABASE_URL` | SQLAlchemy URL (SQLite, MySQL via PyMySQL, …) | `instance/scholarships.db` |
| `SESSION_COOKIE_SECURE` | Set to `1` when served over HTTPS | `0` |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Admin account created by `seed.py` | demo credentials |
| `SEED_DEMO_STUDENT` | Set to `0` to skip the demo student | `1` |

## Deploying to PythonAnywhere
1. Open a **Bash console** and clone the repo: `git clone https://github.com/sarvesh-raam/scholarship-portal.git`
2. Create a virtualenv: `mkvirtualenv --python=python3.11 scholarship-venv && pip install -r scholarship-portal/requirements.txt`
3. Seed the database: `cd scholarship-portal && ADMIN_PASSWORD='<strong password>' python seed.py`
4. **Web** tab → *Add a new web app* → *Manual configuration* → Python 3.11.
5. Set **Virtualenv** to `/home/<username>/.virtualenvs/scholarship-venv`.
6. Edit the **WSGI configuration file** and replace its contents with the snippet at the top of `wsgi.py` (set your own `SECRET_KEY`).
7. Click **Reload**. Free web apps expire after three months — press **"Run until 3 months from today"** on the Web tab to keep the site online.

## Dataset & Metrics
- **Core Entities**: Users (Admins/Students), Scholarships (Schemes), Applications, Finance Records.
- **Calculated KPIs**: Approval rates, financial burn (allotment vs. budget), and eligibility density tracking.

## Contributors
- Sarvesh Raam - Project Lead, Backend Architecture, Database Design, Deployment
- Arunkumar C - UI/UX, Frontend Logic
