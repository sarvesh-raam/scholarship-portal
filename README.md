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
