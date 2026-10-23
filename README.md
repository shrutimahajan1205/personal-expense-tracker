# 💳 ExpenseWise: Personal Expense Tracker Web Application

> **A full-stack, submission-ready Python & Flask web application designed to help individuals, students, and freelancers record, manage, analyze, and optimize their daily financial transactions.**

---

## 🎯 Aim of the Project

- Build a production-grade, full-stack Python web application for personal financial tracking.
- Apply core web development technologies: **Python 3, Flask, SQLite/PostgreSQL (SQLAlchemy ORM), HTML5, CSS3, JavaScript, Bootstrap 5, and Chart.js**.
- Demonstrate end-to-end implementation of:
  - Secure User Authentication and Session Management (`Flask-Login`, `Werkzeug`).
  - Full CRUD operations with multi-criteria filtering and search.
  - Interactive Visual Analytics and charts with dynamic AJAX updates.
  - Category budget tracking with automatic threshold warnings (>80%) and overrun alerts (>100%).
  - Financial reporting and CSV export.
  - Cloud deployment readiness (Render / Railway).

---

## 💼 Supported Use Cases

### 👤 1. For Individual Users
- **Track Daily Spending:** Log income and expenses across various categories (food, bills, commute, health, etc.).
- **Visual Analytics:** Interactive Chart.js charts showing spending breakdowns, monthly comparisons, and daily trends.
- **Budget Control:** Set monthly spending caps and receive visual warnings before overspending.

### 📊 2. For Students
- **Pocket Money & Allowance Tracking:** Log allowance credits and monitor daily campus cafeteria, travel, and leisure spending.
- **Savings Goals:** Keep an eye on the monthly savings rate percentage to build financial discipline.

### 🧮 3. For Freelancers & Small Business Owners
- **Track Business Outflows:** Tag project expenses, software subscriptions, and equipment purchases.
- **Bookkeeping & Tax Planning:** Generate monthly financial statements and export itemized records to CSV with a single click.

---

## ⚙️ Core Features Summary

| Feature | Description |
|---|---|
| **User Authentication** | User Signup, Login, Remember Me, and Logout using `Flask-Login` and `Werkzeug` secure password hashing. |
| **Transaction CRUD** | Add, edit, view, and delete income and expense records (with title, category, date, payment channel, and notes). |
| **Categories & Customization** | Pre-seeded categories with custom colors and icons; ability to create and customize new user-defined categories. |
| **Multi-Criteria Filtering** | Filter transactions by keyword search, preset dates (This Month, Last Month, This Year), custom date ranges, and categories. |
| **Interactive Analytics** | Real-time Chart.js visualizations: Category Doughnut, 6-Month Income vs Expense Bar, 30-Day Trend Line, and Payment Channel breakdown. |
| **Budget Management** | Set category-specific monthly spending limits with progress indicators and automated status alerts (Safe / Warning / Danger). |
| **Export & Printable Reports** | Download filtered ledger as a CSV spreadsheet; print-ready monthly financial statements. |
| **Deployment Ready** | Includes `Procfile`, `render.yaml`, environment configuration, and gunicorn support for instant deployment. |

---

## 🛠️ Technology Stack

- **Backend:** Python 3.13, Flask 3.x, Flask-Login, Flask-SQLAlchemy (ORM), Werkzeug
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Database:** SQLite (default for development), PostgreSQL compatible via `DATABASE_URL`
- **Testing:** Python `unittest` suite
- **Server / Deployment:** Gunicorn WSGI, Render / Railway / Heroku

---

## 📁 Project Directory Structure

```text
personal-expense-tracker/
├── app/
│   ├── __init__.py             # Flask app factory, extension configs, filters
│   ├── models.py               # User, Category, Transaction, Budget models
│   ├── utils.py                # Category initialization & helper utilities
│   ├── routes/
│   │   ├── auth.py             # User signup, login, logout, profile
│   │   ├── main.py             # Main dashboard & financial overview
│   │   ├── expenses.py         # Full CRUD, filters, pagination, CSV export
│   │   ├── analytics.py        # Visual charts page & JSON data API
│   │   └── budgets.py          # Category budget limits & alert system
│   ├── static/
│   │   ├── css/style.css       # Clean, modern responsive stylesheet
│   │   └── js/
│   │       ├── charts.js       # Chart.js initialization & dynamic updates
│   │       └── main.js         # Client-side UI enhancements & validation
│   └── templates/
│       ├── base.html           # Master layout & quick-add modal
│       ├── auth/
│       │   ├── login.html      # Authentication with demo login helper
│       │   └── register.html   # User registration
│       ├── dashboard.html      # Central dashboard with stat cards & widgets
│       ├── expenses/
│       │   ├── index.html      # Transaction ledger with search & filters
│       │   ├── form.html       # Edit / Add transaction form
│       │   └── categories.html # Category management
│       ├── analytics.html      # 4 interactive visual Chart.js graphs
│       ├── budgets.html        # Budget manager & limit progress bars
│       └── reports.html        # Monthly financial statement & print view
├── tests/
│   ├── __init__.py
│   └── test_tracker.py         # Unit & integration tests
├── config.py                   # Development, testing, and cloud configuration
├── run.py                      # Application runner
├── seed.py                     # Realistic demo data populator
├── requirements.txt            # Python dependencies
├── Procfile                    # Cloud process declaration
├── render.yaml                 # Render cloud deployment specification
├── .env.example                # Sample environment variables
└── PROJECT_SUBMISSION_REPORT.md# Academic report & Viva interview preparation
```

---

## 🚀 Quick Start Guide

### 1. Clone or Open the Project
Navigate to the project root directory:
```bash
cd personal-expense-tracker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Realistic Demo Data
Populate the database with a pre-configured demo account and 3 months of sample transactions and budgets:
```bash
python seed.py
```

### 4. Run the Application
```bash
python run.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Account Credentials

For quick evaluation, use the pre-seeded demo user:
- **Email:** `demo@example.com`
- **Password:** `password123`

*(You can also register a brand new user via the Register page; default categories will be initialized automatically.)*

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite:
```bash
python -m unittest tests/test_tracker.py
```
**Test Coverage:**
- User password hashing & validation
- Authentication workflow (Register -> Login -> Logout)
- Transaction CRUD operations & automatic balance calculations
- Category budget threshold calculations (Safe, Warning, Danger)

---

## ☁️ Deployment Instructions

### Deploy to Render
1. Push this repository to GitHub or GitLab.
2. In the Render Dashboard, click **New > Blueprint** and link the repository (uses `render.yaml`).
3. Alternatively, create a **Web Service**:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt && python seed.py`
   - **Start Command:** `gunicorn run:app`

---

## 📄 Academic Project Report

For college viva and project submission, refer to [`PROJECT_SUBMISSION_REPORT.md`](PROJECT_SUBMISSION_REPORT.md) included in this directory.
