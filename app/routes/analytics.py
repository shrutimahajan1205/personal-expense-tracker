from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.models import Transaction, Category, Budget

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics_view():
    today = date.today()
    # List of months for report filter
    months = [
        {"value": i, "name": date(2026, i, 1).strftime("%B")}
        for i in range(1, 13)
    ]
    years = [today.year, today.year - 1]

    return render_template('analytics.html', months=months, years=years, current_month=today.month, current_year=today.year)


@analytics_bp.route('/api/analytics-data')
@login_required
def analytics_data():
    month = request.args.get('month', type=int)
    year = request.args.get('year', date.today().year, type=int)

    # 1. Category breakdown for expenses
    cat_query = db.session.query(
        Category.name,
        Category.color,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(
         Transaction.user_id == current_user.id,
         Transaction.type == 'expense'
     )

    if month:
        cat_query = cat_query.filter(
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        )
    else:
        cat_query = cat_query.filter(db.extract('year', Transaction.date) == year)

    category_results = cat_query.group_by(Category.id).order_by(db.func.sum(Transaction.amount).desc()).all()

    category_labels = [c[0] for c in category_results]
    category_totals = [float(c[2]) for c in category_results]
    category_colors = [c[1] for c in category_results]

    # 2. Monthly Income vs Expenses (Last 6 Months)
    today = date.today()
    months_labels = []
    income_by_month = []
    expense_by_month = []

    for i in range(5, -1, -1):
        # Calculate year and month offset
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        label = date(y, m, 1).strftime('%b %Y')
        months_labels.append(label)

        inc = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'income',
            db.extract('month', Transaction.date) == m,
            db.extract('year', Transaction.date) == y
        ).scalar() or 0.0

        exp = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == 'expense',
            db.extract('month', Transaction.date) == m,
            db.extract('year', Transaction.date) == y
        ).scalar() or 0.0

        income_by_month.append(round(float(inc), 2))
        expense_by_month.append(round(float(exp), 2))

    # 3. Last 30 Days Spending Trend
    thirty_days_ago = today - timedelta(days=29)
    trend_txs = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense',
        Transaction.date >= thirty_days_ago
    ).all()

    trend_dict = {}
    for i in range(30):
        d = (thirty_days_ago + timedelta(days=i)).strftime('%b %d')
        trend_dict[d] = 0.0

    for t in trend_txs:
        d_str = t.date.strftime('%b %d')
        if d_str in trend_dict:
            trend_dict[d_str] += t.amount

    trend_labels = list(trend_dict.keys())
    trend_values = [round(v, 2) for v in trend_dict.values()]

    # 4. Payment Method breakdown
    payment_methods_query = db.session.query(
        Transaction.payment_method,
        db.func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == 'expense'
    )
    if month:
        payment_methods_query = payment_methods_query.filter(
            db.extract('month', Transaction.date) == month,
            db.extract('year', Transaction.date) == year
        )
    pm_results = payment_methods_query.group_by(Transaction.payment_method).all()
    pm_labels = [p[0] or 'Other' for p in pm_results]
    pm_values = [float(p[1]) for p in pm_results]

    return jsonify({
        'categories': {
            'labels': category_labels,
            'data': category_totals,
            'colors': category_colors
        },
        'income_vs_expense': {
            'labels': months_labels,
            'income': income_by_month,
            'expense': expense_by_month
        },
        'spending_trend': {
            'labels': trend_labels,
            'data': trend_values
        },
        'payment_methods': {
            'labels': pm_labels,
            'data': pm_values
        }
    })


@analytics_bp.route('/reports')
@login_required
def reports():
    today = date.today()
    selected_month = request.args.get('month', today.month, type=int)
    selected_year = request.args.get('year', today.year, type=int)

    month_start = date(selected_year, selected_month, 1)
    if selected_month == 12:
        month_end = date(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(selected_year, selected_month + 1, 1) - timedelta(days=1)

    # Monthly transactions
    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= month_start,
        Transaction.date <= month_end
    ).order_by(Transaction.date.asc()).all()

    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0

    # Category summaries
    cat_summary = db.session.query(
        Category.name,
        Category.type,
        db.func.sum(Transaction.amount).label('total'),
        db.func.count(Transaction.id).label('count')
    ).join(Transaction, Transaction.category_id == Category.id)\
     .filter(
         Transaction.user_id == current_user.id,
         Transaction.date >= month_start,
         Transaction.date <= month_end
     ).group_by(Category.id)\
      .order_by(db.func.sum(Transaction.amount).desc()).all()

    month_name = month_start.strftime("%B %Y")

    months = [
        {"value": i, "name": date(2026, i, 1).strftime("%B")}
        for i in range(1, 13)
    ]
    years = [today.year, today.year - 1]

    return render_template(
        'reports.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        savings_rate=savings_rate,
        cat_summary=cat_summary,
        month_name=month_name,
        selected_month=selected_month,
        selected_year=selected_year,
        months=months,
        years=years
    )
