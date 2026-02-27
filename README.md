<div align="center">
  <img src="https://img.shields.io/badge/Fintech-Scholarship%20Pulse-6C63FF?style=for-the-badge&logo=flask&logoColor=white" alt="Scholarship Portal badge" />
  <h1>Scholarship Management & Financial Portal</h1>
  <p><em>From eligibility screening to automated budget tracking — a unified gateway for student success.</em></p>
  <p>
    <a href="https://scholarshipportal.pythonanywhere.com/"><img src="https://img.shields.io/badge/Live%20Demo-Online-brightgreen?style=flat-square&logo=render&logoColor=white" /></a>
    <a href="#-system-lineup"><img src="https://img.shields.io/badge/System-Role%20Based%20Access-9D4EDD?style=flat-square" /></a>
    <a href="#-tech-stack"><img src="https://img.shields.io/badge/Backend-Flask%20%2B%20SQLite-3776AB?style=flat-square&logo=python&logoColor=white" /></a>
    <a href="https://github.com/sarvesh-raam/scholarship-portal"><img src="https://img.shields.io/badge/GitHub-View%20Source-24292F?style=flat-square&logo=github" /></a>
  </p>
</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/sarvesh-raam/scholarship-portal/main/app/static/img/hero-preview.png" alt="Hero Dashboard" width="95%" onerror="this.src='https://images.unsplash.com/photo-1523050853063-bd8012fec21b?q=80&w=1000&auto=format&fit=crop'"/>
</div>

<div align="center">
  <table>
    <tr>
      <td><strong>🔐 Security</strong><br/>Bcrypt Hashing • RBAC • Session Logs</td>
      <td><strong>🧠 Intelligence</strong><br/>Automated Eligibility Checks</td>
      <td><strong>🎨 UI/UX</strong><br/>Modern Clean • Mobile Responsive</td>
      <td><strong>💰 Finance</strong><br/>Budget Tracking • Allotment Reports</td>
    </tr>
  </table>
</div>

---

## 📌 Table of Contents
1. [Why This Project?](#-why-this-project)
2. [System Lineup](#-system-lineup)
3. [Solution Blueprint](#-solution-blueprint)
4. [Dataset & Metrics](#-dataset--metrics)
5. [Quickstart Guide](#-quickstart-guide)
6. [Feature Deep Dive](#-feature-deep-dive)
7. [Design Philosophy](#-design-philosophy)
8. [Contributors](#-contributors)
9. [Resources](#-resources)

---

## 🌈 Experience Highlights
<div align="center">
  <table>
    <tr>
      <td><strong>✨ Narrative-Driven UX</strong><br/>Guided application flows ensure students never miss a required document.</td>
      <td><strong>⚡ Instant Approval</strong><br/>Admins can review, comment, and verify CGPA requirements in one click.</td>
    </tr>
    <tr>
      <td><strong>🛰 Live Financials</strong><br/>Real-time DAX-style calculations for remaining scholarship budgets.</td>
      <td><strong>🧩 Scalable Core</strong><br/>Easily plug in new scholarship schemes (OBC/SC/ST/General) via the Admin panel.</td>
    </tr>
  </table>
</div>

---

## 🎯 Why This Project?
- **Single source of truth** for student financial aid, applications, and payouts.
- **Decision-ready insights** identifying which scholarship schemes are most impactful.
- **Zero-Friction Deployment**: Fully optimized for PythonAnywhere with a persistent SQLite engine.
- **Audit-Ready**: Transparent tracking of who approved which application and when.

---

## 📊 System Lineup
| Experience | Capabilities | Status |
| --- | --- | --- |
| **Admin Command Center** | Budget oversight, Scheme creation, Application review | ✅ Production |
| **Student Gateway** | Eligibility search, CGPA verification, Application tracking | ✅ Production |
| **Finance Engine** | Real-time budget recalculation & balance tracking | ✅ Production |
| **Auth Logic** | Secure Login, Role Redirection, Session Management | ✅ Production |

---

## 🧱 Solution Blueprint
```
scholarship-portal/
├─ app/
│  ├─ static/                  # CSS, Images, JS
│  ├─ templates/               # Jinja2 HTML Views
│  ├─ models.py                # Database Schema (ORM)
│  └─ routes.py                # Business Logic & Redirection
├─ instance/                   # Persistent SQLite Database
├─ requirements.txt            # Production Dependencies
├─ run.py                      # Application Entry Point
├─ seed.py                     # Database Initializer/Mock Data
└─ README.md
```

---

## 📋 Dataset & Metrics
**Core Entities:** Users (Admins/Students), Scholarships (Schemes), Applications, Finance Records.

**Core Data Points**
- **Scholarships**: Name, Category, Eligibility, Amount, Deadline
- **Applications**: Student Link, Status (Pending/Approved/Rejected), CGPA, Remarks
- **Finance**: Total Budget, Allocated Funds, Remaining Balance

**Calculated KPIs**
- **Approval Rate**: Percentage of processed student applications.
- **Financial Burn**: Current allotment vs. total scheme budget.
- **Eligibility Density**: Distribution of students across various categories (SC/ST/General).

---

## ⚙️ Quickstart Guide
1. **Clone**
   ```bash
   git clone https://github.com/sarvesh-raam/scholarship-portal.git
   cd scholarship-portal
   ```
2. **Launch Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Initialize & Run**
   ```bash
   python seed.py  # Created Admin & Initial Scholarships
   python run.py
   ```

### 🐍 Production Credentials
- **Admin Access**: `admin@example.com` | `admin123`
- **Student Access**: `student@example.com` | `student123`

---

## 🔍 Feature Deep Dive

<details>
  <summary>1️⃣ Smart Eligibility Filter — <em>The right aid for the right student</em></summary>
  <ul>
    <li>Automatic filtering based on student category (SC/ST/EBC).</li>
    <li>Minimum CGPA validation prior to application submission.</li>
    <li>Income limit checks to ensure social-equity distribution.</li>
  </ul>
</details>

<details>
  <summary>2️⃣ Admin Review Studio — <em>Decision-ready transparency</em></summary>
  <ul>
    <li>Real-time table view of all un-reviewed applications.</li>
    <li>Inline status toggle (Approve/Reject) with reviewer remarks.</li>
    <li>Automatic timestamping of all review actions for audit trails.</li>
  </ul>
</details>

<details>
  <summary>3️⃣ Finance Dashboard — <em>Protecting the budget</em></summary>
  <ul>
    <li>Dynamic progress bars showing budget consumption.</li>
    <li>Automatic lockdown of approvals if the scheme budget is exceeded.</li>
    <li>Year-over-year reporting on fund distribution.</li>
  </ul>
</details>

---

## 🤝 Contributors
| Contributor | Focus |
| :---: | :--- |
| <a href="https://github.com/sarvesh-raam"><img src="https://github.com/sarvesh-raam.png" width="90" /></a><br/>[Sarvesh Raam](https://github.com/sarvesh-raam) | **Project Lead** • Backend Architecture • Database Design • Deployment |
| <a href="https://github.com/arunkumarc05"><img src="https://github.com/arunkumarc05.png" width="90" /></a><br/>[Arunkumar C](https://github.com/arunkumarc05) | **Collaborator** • UI Polishing • Storytelling Content • Frontend Logic |

---

## 📚 Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/)
- [PythonAnywhere Deployment](https://help.pythonanywhere.com/pages/Flask/)

<div align="center">
  <p><em>Crafted with care for educational equity. 🎓</em></p>
</div>
