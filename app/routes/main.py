from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import date, datetime
from app import db
from app.models import Transaction, Category, Budget

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    first_of_month = date(today.year, today.month, 1)

    # Monthly figures
    monthly_income = current_user.total_income(start_date=first_of_month)
    monthly_expense = current_user.total_expense(start_date=first_of_month)
    monthly_savings = round(monthly_income - monthly_expense, 2)
    savings_rate = round((monthly_savings / monthly_income * 100), 1) if monthly_income > 0 else 0.0

    # All-time figures
    total_balance = current_user.net_balance()
    all_time_income = current_user.total_income()
    all_time_expense = current_user.total_expense()

    # Recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc(), Transaction.id.desc())\
        .limit(6).all()

    # Active budgets for current month
    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=today.month,
        year=today.year
    ).all()

    # Active budget alerts (warning or danger)
    budget_alerts = [b for b in budgets if b.status() in ['warning', 'danger']]

    # Categories for quick add modal
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    ).order_by(Category.name).all()

    # Category expense summary for current month
    cat_summary = db.session.query(
        Category.name,
        Category.color,
        Category.icon,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(
         Transaction.user_id == current_user.id,
         Transaction.type == 'expense',
         Transaction.date >= first_of_month
     ).group_by(Category.id)\
      .order_by(db.func.sum(Transaction.amount).desc())\
      .limit(5).all()

    return render_template(
        'dashboard.html',
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_savings=monthly_savings,
        savings_rate=savings_rate,
        total_balance=total_balance,
        all_time_income=all_time_income,
        all_time_expense=all_time_expense,
        recent_transactions=recent_transactions,
        budgets=budgets,
        budget_alerts=budget_alerts,
        categories=categories,
        cat_summary=cat_summary,
        today=today
    )
