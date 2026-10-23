from app import db
from app.models import Category

DEFAULT_CATEGORIES = [
    # Expenses
    {"name": "Food & Dining", "type": "expense", "icon": "bi-cup-hot-fill", "color": "#fd7e14"},
    {"name": "Travel & Commute", "type": "expense", "icon": "bi-airplane-fill", "color": "#0dcaf0"},
    {"name": "Bills & Utilities", "type": "expense", "icon": "bi-receipt", "color": "#dc3545"},
    {"name": "Entertainment", "type": "expense", "icon": "bi-controller", "color": "#6f42c1"},
    {"name": "Groceries", "type": "expense", "icon": "bi-cart-check-fill", "color": "#198754"},
    {"name": "Shopping", "type": "expense", "icon": "bi-bag-heart-fill", "color": "#e83e8c"},
    {"name": "Health & Medical", "type": "expense", "icon": "bi-heart-pulse-fill", "color": "#d63384"},
    {"name": "Education & Books", "type": "expense", "icon": "bi-mortarboard-fill", "color": "#20c997"},
    {"name": "Personal Care", "type": "expense", "icon": "bi-person-heart", "color": "#ffc107"},
    {"name": "Other Expense", "type": "expense", "icon": "bi-three-dots", "color": "#6c757d"},
    # Incomes
    {"name": "Salary / Job", "type": "income", "icon": "bi-cash-coin", "color": "#198754"},
    {"name": "Freelance / Projects", "type": "income", "icon": "bi-laptop", "color": "#0d6efd"},
    {"name": "Allowance / Pocket Money", "type": "income", "icon": "bi-wallet2", "color": "#20c997"},
    {"name": "Investments & Dividends", "type": "income", "icon": "bi-graph-up-arrow", "color": "#0dcaf0"},
    {"name": "Other Income", "type": "income", "icon": "bi-piggy-bank-fill", "color": "#ffc107"}
]

def ensure_default_categories_for_user(user_id):
    """Ensure standard categories exist for the user."""
    existing_count = Category.query.filter_by(user_id=user_id).count()
    if existing_count == 0:
        for cat_data in DEFAULT_CATEGORIES:
            cat = Category(
                name=cat_data["name"],
                type=cat_data["type"],
                icon=cat_data["icon"],
                color=cat_data["color"],
                user_id=user_id
            )
            db.session.add(cat)
        db.session.commit()
