from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
import csv
import io
from app import db
from app.models import Transaction, Category, Budget

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    tx_type = request.args.get('type', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    preset = request.args.get('preset', 'all')

    query = Transaction.query.filter_by(user_id=current_user.id)

    # Preset date filters
    today = date.today()
    if preset == 'this_month':
        query = query.filter(Transaction.date >= date(today.year, today.month, 1))
    elif preset == 'last_month':
        first_this_month = date(today.year, today.month, 1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = date(last_month_end.year, last_month_end.month, 1)
        query = query.filter(Transaction.date >= last_month_start, Transaction.date <= last_month_end)
    elif preset == 'this_year':
        query = query.filter(Transaction.date >= date(today.year, 1, 1))

    # Custom date range
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            pass

    # Filter by category
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    # Filter by type (income / expense)
    if tx_type in ['income', 'expense']:
        query = query.filter(Transaction.type == tx_type)

    # Search query
    if search:
        query = query.filter(
            (Transaction.title.ilike(f'%{search}%')) |
            (Transaction.notes.ilike(f'%{search}%'))
        )

    # Order and paginate
    pagination = query.order_by(Transaction.date.desc(), Transaction.id.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    transactions = pagination.items

    # Calculation totals for current filtered view
    all_filtered = query.all()
    filtered_income = sum(t.amount for t in all_filtered if t.type == 'income')
    filtered_expense = sum(t.amount for t in all_filtered if t.type == 'expense')
    filtered_net = filtered_income - filtered_expense

    # Categories list for dropdown
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    ).order_by(Category.name).all()

    return render_template(
        'expenses/index.html',
        transactions=transactions,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=category_id,
        selected_type=tx_type,
        start_date=start_date_str,
        end_date=end_date_str,
        preset=preset,
        filtered_income=filtered_income,
        filtered_expense=filtered_expense,
        filtered_net=filtered_net
    )


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    ).order_by(Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount_str = request.form.get('amount', '0')
        tx_type = request.form.get('type', 'expense')
        category_id = request.form.get('category_id', type=int)
        date_str = request.form.get('date', '')
        payment_method = request.form.get('payment_method', 'UPI / GPay')
        notes = request.form.get('notes', '').strip()

        if not title or not category_id or not amount_str:
            flash('Title, amount, and category are required.', 'danger')
            return redirect(request.referrer or url_for('expenses.index'))

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return redirect(request.referrer or url_for('expenses.index'))
        except ValueError:
            flash('Invalid amount entered.', 'danger')
            return redirect(request.referrer or url_for('expenses.index'))

        tx_date = date.today()
        if date_str:
            try:
                tx_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                tx_date = date.today()

        transaction = Transaction(
            user_id=current_user.id,
            category_id=category_id,
            title=title,
            amount=amount,
            type=tx_type,
            date=tx_date,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(transaction)
        db.session.commit()

        # Check budget status for alert
        if tx_type == 'expense':
            budget = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=category_id,
                month=tx_date.month,
                year=tx_date.year
            ).first()
            if budget and budget.get_raw_percentage() >= 100:
                flash(f'⚠️ Warning: You have exceeded your budget for {budget.category.name}!', 'danger')
            elif budget and budget.get_raw_percentage() >= 80:
                flash(f'⚠️ Notice: You have used {budget.get_percentage()}% of your budget for {budget.category.name}.', 'warning')
            else:
                flash(f'Successfully logged {tx_type}: {title} ({current_user.currency}{amount:,.2f})', 'success')
        else:
            flash(f'Successfully logged income: {title} ({current_user.currency}{amount:,.2f})', 'success')

        return redirect(request.referrer or url_for('expenses.index'))

    return render_template('expenses/form.html', categories=categories, transaction=None, is_edit=False)


@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    ).order_by(Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount_str = request.form.get('amount', '0')
        tx_type = request.form.get('type', 'expense')
        category_id = request.form.get('category_id', type=int)
        date_str = request.form.get('date', '')
        payment_method = request.form.get('payment_method', 'UPI / GPay')
        notes = request.form.get('notes', '').strip()

        if not title or not category_id or not amount_str:
            flash('Title, amount, and category are required.', 'danger')
            return render_template('expenses/form.html', categories=categories, transaction=transaction, is_edit=True)

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'danger')
                return render_template('expenses/form.html', categories=categories, transaction=transaction, is_edit=True)
        except ValueError:
            flash('Invalid amount entered.', 'danger')
            return render_template('expenses/form.html', categories=categories, transaction=transaction, is_edit=True)

        tx_date = transaction.date
        if date_str:
            try:
                tx_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        transaction.title = title
        transaction.amount = amount
        transaction.type = tx_type
        transaction.category_id = category_id
        transaction.date = tx_date
        transaction.payment_method = payment_method
        transaction.notes = notes

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('expenses/form.html', categories=categories, transaction=transaction, is_edit=True)


@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    title = transaction.title
    db.session.delete(transaction)
    db.session.commit()
    flash(f'Transaction "{title}" deleted successfully.', 'info')
    return redirect(request.referrer or url_for('expenses.index'))


@expenses_bp.route('/export')
@login_required
def export_csv():
    # Export transactions to CSV (respects current search/filter or exports all)
    category_id = request.args.get('category_id', type=int)
    tx_type = request.args.get('type', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    query = Transaction.query.filter_by(user_id=current_user.id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if tx_type in ['income', 'expense']:
        query = query.filter(Transaction.type == tx_type)
    if start_date_str:
        try:
            query = query.filter(Transaction.date >= datetime.strptime(start_date_str, '%Y-%m-%d').date())
        except ValueError:
            pass
    if end_date_str:
        try:
            query = query.filter(Transaction.date <= datetime.strptime(end_date_str, '%Y-%m-%d').date())
        except ValueError:
            pass

    transactions = query.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Title', 'Type', 'Category', 'Amount', 'Currency', 'Payment Method', 'Notes'])

    for t in transactions:
        writer.writerow([
            t.id,
            t.date.strftime('%Y-%m-%d'),
            t.title,
            t.type.capitalize(),
            t.category.name if t.category else 'Uncategorized',
            t.amount,
            current_user.currency,
            t.payment_method,
            t.notes or ''
        ])

    csv_data = output.getvalue()
    filename = f"expenses_export_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


@expenses_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        cat_type = request.form.get('type', 'expense')
        icon = request.form.get('icon', 'bi-tag')
        color = request.form.get('color', '#0d6efd')

        if not name:
            flash('Category name is required.', 'danger')
        else:
            category = Category(
                name=name,
                type=cat_type,
                icon=icon,
                color=color,
                user_id=current_user.id
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{name}" added successfully.', 'success')

        return redirect(url_for('expenses.manage_categories'))

    categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.user_id == None)
    ).order_by(Category.name).all()

    return render_template('expenses/categories.html', categories=categories)
