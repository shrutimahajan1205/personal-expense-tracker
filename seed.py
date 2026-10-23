from app import create_app, db
from app.models import User, Category, Transaction, Budget
from app.utils import ensure_default_categories_for_user
from datetime import date, timedelta
import random

def seed_database():
    app = create_app()
    with app.app_context():
        print("[*] Seeding database...")
        db.create_all()

        # Check if demo user already exists
        demo_user = User.query.filter_by(email="demo@example.com").first()
        if not demo_user:
            demo_user = User(
                username="demo_user",
                email="demo@example.com",
                currency="₹"
            )
            demo_user.set_password("password123")
            db.session.add(demo_user)
            db.session.commit()
            print("[+] Created Demo User: demo@example.com / password123")

        # Ensure default categories
        ensure_default_categories_for_user(demo_user.id)
        categories = {c.name: c for c in Category.query.filter_by(user_id=demo_user.id).all()}

        # Clear existing transactions & budgets for a fresh demo state if any
        Transaction.query.filter_by(user_id=demo_user.id).delete()
        Budget.query.filter_by(user_id=demo_user.id).delete()
        db.session.commit()

        today = date.today()
        current_month = today.month
        current_year = today.year

        # Seed Transactions across past 3 months
        sample_transactions = []

        # Current Month Incomes
        if "Salary / Job" in categories:
            sample_transactions.append(Transaction(
                user_id=demo_user.id,
                category_id=categories["Salary / Job"].id,
                title="Monthly Software Engineering Salary",
                amount=65000.0,
                type="income",
                date=date(current_year, current_month, 1),
                payment_method="Net Banking",
                notes="Credited from TechCorp Labs"
            ))

        if "Freelance / Projects" in categories:
            sample_transactions.append(Transaction(
                user_id=demo_user.id,
                category_id=categories["Freelance / Projects"].id,
                title="Frontend Redesign Client Project",
                amount=18500.0,
                type="income",
                date=date(current_year, current_month, min(12, today.day)),
                payment_method="UPI / GPay",
                notes="Milestone payment for client website"
            ))

        # Current Month Expenses
        expense_templates = [
            ("Weekly Supermarket Grocery", "Groceries", 2800.0, 3, "Credit/Debit Card", "Vegetables, dairy, and household essentials"),
            ("High-speed Fiber Broadband Bill", "Bills & Utilities", 1199.0, 4, "UPI / GPay", "Monthly 200Mbps connection"),
            ("Electricity & Water Utility Bill", "Bills & Utilities", 2450.0, 6, "Net Banking", "State power board bill payment"),
            ("Metro Smart Card Recharge", "Travel & Commute", 1000.0, 7, "UPI / GPay", "Monthly office commute travel pass"),
            ("Cab to Airport / Tech Park", "Travel & Commute", 650.0, 9, "UPI / GPay", "Ride hailing fare"),
            ("Team Lunch & Cafe Outing", "Food & Dining", 1850.0, 10, "Credit/Debit Card", "Weekend lunch with colleagues"),
            ("Coffee & Bakery Snacks", "Food & Dining", 420.0, 12, "UPI / GPay", "Starbucks cold brew & pastry"),
            ("Weekly Pantry Restock", "Groceries", 2400.0, 14, "UPI / GPay", "Organic grains and groceries"),
            ("Dinner with College Friends", "Food & Dining", 2800.0, 15, "Credit/Debit Card", "Barbeque Nation dinner"),
            ("Netflix & Spotify Premium", "Entertainment", 949.0, 16, "Credit/Debit Card", "Monthly digital entertainment subscription"),
            ("Cinema IMAX Movie Tickets", "Entertainment", 1200.0, 18, "UPI / GPay", "Weekend movie with popcorn"),
            ("Gaming / Steam Sale Purchase", "Entertainment", 1450.0, 19, "Credit/Debit Card", "Indie game bundle purchase"),
            ("Full Body Health Checkup & Labs", "Health & Medical", 1600.0, 20, "UPI / GPay", "Annual preventative diagnostics"),
            ("Python & Web Dev Reference Books", "Education & Books", 1250.0, 21, "UPI / GPay", "Clean Code & System Design books"),
            ("Clothing & Footwear Purchase", "Shopping", 3400.0, min(today.day, 22), "Credit/Debit Card", "Seasonal wardrobe upgrade"),
            ("Daily Cafeteria Meal", "Food & Dining", 350.0, today.day, "Cash", "Lunch at campus food court")
        ]

        for title, cat_name, amt, day_num, p_method, notes in expense_templates:
            if cat_name in categories:
                # Keep day within valid month limits and not future
                safe_day = max(1, min(day_num, today.day))
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories[cat_name].id,
                    title=title,
                    amount=amt,
                    type="expense",
                    date=date(current_year, current_month, safe_day),
                    payment_method=p_method,
                    notes=notes
                ))

        # Previous 2 months historical transactions (for charts trend)
        for offset in [1, 2]:
            m = current_month - offset
            y = current_year
            if m <= 0:
                m += 12
                y -= 1

            if "Salary / Job" in categories:
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories["Salary / Job"].id,
                    title="Monthly Salary Credit",
                    amount=65000.0,
                    type="income",
                    date=date(y, m, 1),
                    payment_method="Net Banking",
                    notes="Direct bank deposit"
                ))

            if "Groceries" in categories:
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories["Groceries"].id,
                    title="Monthly Groceries",
                    amount=7200.0,
                    type="expense",
                    date=date(y, m, 5),
                    payment_method="Credit/Debit Card",
                    notes="Mart monthly purchase"
                ))

            if "Food & Dining" in categories:
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories["Food & Dining"].id,
                    title="Dining & Food Delivery",
                    amount=5800.0,
                    type="expense",
                    date=date(y, m, 12),
                    payment_method="UPI / GPay",
                    notes="Zomato & Dineout"
                ))

            if "Bills & Utilities" in categories:
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories["Bills & Utilities"].id,
                    title="Utility & Maintenance Bills",
                    amount=4200.0,
                    type="expense",
                    date=date(y, m, 8),
                    payment_method="Net Banking",
                    notes="Apartment maintenance & electric"
                ))

            if "Travel & Commute" in categories:
                sample_transactions.append(Transaction(
                    user_id=demo_user.id,
                    category_id=categories["Travel & Commute"].id,
                    title="Monthly Commute Expenses",
                    amount=2800.0,
                    type="expense",
                    date=date(y, m, 15),
                    payment_method="UPI / GPay",
                    notes="Fuel and metro"
                ))

        db.session.add_all(sample_transactions)

        # Set Realistic Budgets for Current Month
        # 1. Food & Dining limit: ₹7,000 (spent ~₹5,420 -> ~77% warning threshold)
        if "Food & Dining" in categories:
            db.session.add(Budget(
                user_id=demo_user.id,
                category_id=categories["Food & Dining"].id,
                monthly_limit=6000.0,
                month=current_month,
                year=current_year
            ))

        # 2. Entertainment limit: ₹3,000 (spent ~₹3,599 -> Danger exceeded alert!)
        if "Entertainment" in categories:
            db.session.add(Budget(
                user_id=demo_user.id,
                category_id=categories["Entertainment"].id,
                monthly_limit=3000.0,
                month=current_month,
                year=current_year
            ))

        # 3. Groceries limit: ₹8,000 (spent ~₹5,200 -> Safe)
        if "Groceries" in categories:
            db.session.add(Budget(
                user_id=demo_user.id,
                category_id=categories["Groceries"].id,
                monthly_limit=8000.0,
                month=current_month,
                year=current_year
            ))

        # 4. Bills & Utilities limit: ₹5,000 (spent ~₹3,649 -> Safe)
        if "Bills & Utilities" in categories:
            db.session.add(Budget(
                user_id=demo_user.id,
                category_id=categories["Bills & Utilities"].id,
                monthly_limit=5000.0,
                month=current_month,
                year=current_year
            ))

        db.session.commit()
        print("[+] Sample transactions, realistic categories, and budget targets populated successfully!")
        print(">> You can now run 'python run.py' and log in with:")
        print("   Email:    demo@example.com")
        print("   Password: password123")

if __name__ == '__main__':
    seed_database()
