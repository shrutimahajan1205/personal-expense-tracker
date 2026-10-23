from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils import ensure_default_categories_for_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        currency = request.form.get('currency', '₹')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Please choose another.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered. Please log in.', 'danger')
            return render_template('auth/register.html')

        user = User(username=username, email=email, currency=currency)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Seed standard default categories for new user
        ensure_default_categories_for_user(user.id)

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('login_id', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not username_or_email or not password:
            flash('Please enter both username/email and password.', 'danger')
            return render_template('auth/login.html')

        # Find by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Ensure categories exist
            ensure_default_categories_for_user(user.id)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        currency = request.form.get('currency', current_user.currency)
        new_password = request.form.get('new_password', '').strip()

        current_user.currency = currency
        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('profile.html')
            current_user.set_password(new_password)
            flash('Password updated successfully.', 'success')

        db.session.commit()
        flash('Profile settings updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html')
