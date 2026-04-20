# Scholarship Management and Financial Portal

From eligibility screening to automated budget tracking, this platform serves as a unified gateway for student financial aid management and oversight.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=flat-square&logo=render&logoColor=white)](https://scholarshipportal.pythonanywhere.com/)
[![Backend](https://img.shields.io/badge/Backend-Flask%20%2B%20SQLite-3776AB?style=flat-square&logo=python&logoColor=white)](#)

---

## Executive Summary
This portal is designed to provide a single source of truth for student financial aid, applications, and payouts. It offers decision-ready insights into scholarship impact and features a zero-friction deployment optimized for production environments.

## Deployment Proof
Deployed and running in production on PythonAnywhere: [View Live Portal](https://scholarshipportal.pythonanywhere.com/)

## Architecture and System Design
The application follows a traditional Model-View-Controller (MVC) architectural pattern, clearly separating backend logic from frontend presentation.

- **Frontend**: HTML5, CSS3, and Jinja2 templating for dynamic rendering.
- **Backend Framework**: Python Flask handling routing, middleware, and business logic.
- **Database**: SQLite (Development/Production) via SQLAlchemy ORM.
- **Authentication**: Bcrypt for secure password hashing and Role-Based Access Control (RBAC).

## Core Capabilities
- **Admin Command Center**: Complete budget oversight, scheme creation, and application review processes.
- **Student Gateway**: Real-time eligibility search, CGPA verification, and application status tracking.
- **Finance Engine**: Automated budget recalculation and live balance tracking across scholarship schemes.
- **Smart Eligibility Filter**: Automatic filtering based on student category, income limit checks, and minimum CGPA validation.

## Technical Structure
```text
scholarship-portal/
├── app/
│   ├── static/                  # CSS, Images, JS
│   ├── templates/               # Jinja2 HTML Views
│   ├── models.py                # Database Schema (ORM)
│   └── routes.py                # Business Logic & Redirection
├── instance/                    # Persistent Database
├── requirements.txt             # Production Dependencies
└── run.py                       # Application Entry Point
```

## Quickstart Guide

### 1. Clone
```bash
git clone https://github.com/sarvesh-raam/scholarship-portal.git
cd scholarship-portal
```

### 2. Launch Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize and Run
```bash
python seed.py
python run.py
```

## Dataset & Metrics
- **Core Entities**: Users (Admins/Students), Scholarships (Schemes), Applications, Finance Records.
- **Calculated KPIs**: Approval rates, financial burn (allotment vs. budget), and eligibility density tracking.

## Contributors
- Sarvesh Raam - Project Lead, Backend Architecture, Database Design, Deployment
- Arunkumar C - UI/UX, Frontend Logic
