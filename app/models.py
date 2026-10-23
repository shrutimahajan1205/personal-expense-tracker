from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    currency = db.Column(db.String(10), default='₹', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def total_income(self, start_date=None, end_date=None):
        query = Transaction.query.filter_by(user_id=self.id, type='income')
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == 'income'
        )
        if start_date:
            total = total.filter(Transaction.date >= start_date)
        if end_date:
            total = total.filter(Transaction.date <= end_date)
        result = total.scalar()
        return round(result or 0.0, 2)

    def total_expense(self, start_date=None, end_date=None):
        total = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.id,
            Transaction.type == 'expense'
        )
        if start_date:
            total = total.filter(Transaction.date >= start_date)
        if end_date:
            total = total.filter(Transaction.date <= end_date)
        result = total.scalar()
        return round(result or 0.0, 2)

    def net_balance(self, start_date=None, end_date=None):
        return round(self.total_income(start_date, end_date) - self.total_expense(start_date, end_date), 2)

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(10), nullable=False, default='expense') # 'expense' or 'income'
    icon = db.Column(db.String(64), default='bi-tag') # Bootstrap icon class
    color = db.Column(db.String(20), default='#0d6efd') # Hex color
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # None = system default

    transactions = db.relationship('Transaction', backref='category', lazy='dynamic')
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False, default='expense') # 'expense' or 'income'
    date = db.Column(db.Date, nullable=False, default=date.today)
    payment_method = db.Column(db.String(30), default='UPI / GPay')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'amount': self.amount,
            'type': self.type,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_icon': self.category.icon if self.category else 'bi-tag',
            'category_color': self.category.color if self.category else '#6c757d',
            'date': self.date.strftime('%Y-%m-%d'),
            'payment_method': self.payment_method,
            'notes': self.notes or ''
        }

    def __repr__(self):
        return f'<Transaction {self.title}: {self.type} {self.amount}>'


class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False) # 1-12
    year = db.Column(db.Integer, nullable=False) # e.g. 2026
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_spent_amount(self):
        start_date = date(self.year, self.month, 1)
        if self.month == 12:
            end_date = date(self.year + 1, 1, 1)
        else:
            end_date = date(self.year, self.month + 1, 1)

        spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == self.user_id,
            Transaction.category_id == self.category_id,
            Transaction.type == 'expense',
            Transaction.date >= start_date,
            Transaction.date < end_date
        ).scalar()
        return round(spent or 0.0, 2)

    def get_percentage(self):
        spent = self.get_spent_amount()
        if self.monthly_limit <= 0:
            return 100.0 if spent > 0 else 0.0
        return round(min((spent / self.monthly_limit) * 100.0, 100.0), 1)

    def get_raw_percentage(self):
        spent = self.get_spent_amount()
        if self.monthly_limit <= 0:
            return 100.0 if spent > 0 else 0.0
        return round((spent / self.monthly_limit) * 100.0, 1)

    def status(self):
        pct = self.get_raw_percentage()
        if pct >= 100:
            return 'danger' # Over budget
        elif pct >= 80:
            return 'warning' # Approaching limit
        return 'success' # Safe

    def __repr__(self):
        return f'<Budget Category={self.category_id} Limit={self.monthly_limit} Month={self.month}/{self.year}>'
