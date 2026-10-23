from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from app import db
from app.models import Budget, Category

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@budgets_bp.route('/', methods=['GET'])
@login_required
def index():
    today = date.today()
    selected_month = request.args.get('month', today.month, type=int)
    selected_year = request.args.get('year', today.year, type=int)

    budgets = Budget.query.filter_by(
        user_id=current_user.id,
        month=selected_month,
        year=selected_year
    ).all()

    # Expense categories available for budget setting
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None),
        Category.type == 'expense'
    ).order_by(Category.name).all()

    # Calculate overall budget summary
    total_budgeted = sum(b.monthly_limit for b in budgets)
    total_spent_in_budgets = sum(b.get_spent_amount() for b in budgets)
    total_remaining = total_budgeted - total_spent_in_budgets
    overall_percentage = round((total_spent_in_budgets / total_budgeted * 100), 1) if total_budgeted > 0 else 0.0

    months = [
        {"value": i, "name": date(2026, i, 1).strftime("%B")}
        for i in range(1, 13)
    ]
    years = [today.year, today.year - 1]

    return render_template(
        'budgets.html',
        budgets=budgets,
        categories=categories,
        selected_month=selected_month,
        selected_year=selected_year,
        months=months,
        years=years,
        total_budgeted=total_budgeted,
        total_spent_in_budgets=total_spent_in_budgets,
        total_remaining=total_remaining,
        overall_percentage=overall_percentage
    )


@budgets_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    category_id = request.form.get('category_id', type=int)
    limit_str = request.form.get('monthly_limit', '0')
    month = request.form.get('month', date.today().month, type=int)
    year = request.form.get('year', date.today().year, type=int)

    if not category_id or not limit_str:
        flash('Category and monthly limit are required.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    try:
        limit = float(limit_str)
        if limit <= 0:
            flash('Limit must be greater than zero.', 'danger')
            return redirect(url_for('budgets.index', month=month, year=year))
    except ValueError:
        flash('Invalid budget limit.', 'danger')
        return redirect(url_for('budgets.index', month=month, year=year))

    # Check if budget already exists for this category/month/year
    existing_budget = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        month=month,
        year=year
    ).first()

    if existing_budget:
        existing_budget.monthly_limit = limit
        flash(f'Updated budget limit for {existing_budget.category.name} to {current_user.currency}{limit:,.2f}.', 'success')
    else:
        new_budget = Budget(
            user_id=current_user.id,
            category_id=category_id,
            monthly_limit=limit,
            month=month,
            year=year
        )
        db.session.add(new_budget)
        flash(f'Budget limit set successfully!', 'success')

    db.session.commit()
    return redirect(url_for('budgets.index', month=month, year=year))


@budgets_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    budget = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    cat_name = budget.category.name
    month = budget.month
    year = budget.year
    db.session.delete(budget)
    db.session.commit()
    flash(f'Budget for {cat_name} removed.', 'info')
    return redirect(url_for('budgets.index', month=month, year=year))
