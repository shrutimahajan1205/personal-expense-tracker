import unittest
from datetime import date
from app import create_app, db
from app.models import User, Category, Transaction, Budget
from app.utils import ensure_default_categories_for_user
from config import TestConfig

class ExpenseTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_password_hashing(self):
        u = User(username='testuser', email='test@example.com')
        u.set_password('mysecretpass')
        self.assertFalse(u.check_password('wrongpass'))
        self.assertTrue(u.check_password('mysecretpass'))

    def test_default_categories_creation(self):
        u = User(username='catuser', email='cat@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        ensure_default_categories_for_user(u.id)
        categories = Category.query.filter_by(user_id=u.id).all()
        self.assertGreater(len(categories), 5)
        names = [c.name for c in categories]
        self.assertIn('Food & Dining', names)
        self.assertIn('Bills & Utilities', names)
        self.assertIn('Salary / Job', names)

    def test_transaction_crud_and_balances(self):
        u = User(username='financeuser', email='finance@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        c_exp = Category(name='Food', type='expense', user_id=u.id)
        c_inc = Category(name='Salary', type='income', user_id=u.id)
        db.session.add_all([c_exp, c_inc])
        db.session.commit()

        # Add Income
        t1 = Transaction(
            user_id=u.id, category_id=c_inc.id, title='Monthly Stipend',
            amount=20000.0, type='income', date=date.today()
        )
        # Add Expenses
        t2 = Transaction(
            user_id=u.id, category_id=c_exp.id, title='Groceries',
            amount=4500.0, type='expense', date=date.today()
        )
        t3 = Transaction(
            user_id=u.id, category_id=c_exp.id, title='Cafe Lunch',
            amount=500.0, type='expense', date=date.today()
        )
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # Test Totals
        self.assertEqual(u.total_income(), 20000.0)
        self.assertEqual(u.total_expense(), 5000.0)
        self.assertEqual(u.net_balance(), 15000.0)

        # Delete an expense
        db.session.delete(t3)
        db.session.commit()
        self.assertEqual(u.total_expense(), 4500.0)
        self.assertEqual(u.net_balance(), 15500.0)

    def test_budget_thresholds(self):
        u = User(username='budgetuser', email='budget@example.com')
        u.set_password('password123')
        db.session.add(u)
        db.session.commit()

        c = Category(name='Dining', type='expense', user_id=u.id)
        db.session.add(c)
        db.session.commit()

        today = date.today()
        b = Budget(user_id=u.id, category_id=c.id, monthly_limit=1000.0, month=today.month, year=today.year)
        db.session.add(b)
        db.session.commit()

        # Spent 0 -> Status 'success'
        self.assertEqual(b.status(), 'success')
        self.assertEqual(b.get_percentage(), 0.0)

        # Spend 850 -> Status 'warning' (85%)
        t = Transaction(user_id=u.id, category_id=c.id, title='Dinner', amount=850.0, type='expense', date=today)
        db.session.add(t)
        db.session.commit()
        self.assertEqual(b.status(), 'warning')
        self.assertEqual(b.get_raw_percentage(), 85.0)

        # Spend another 300 -> Total 1150 -> Status 'danger' (>100%)
        t2 = Transaction(user_id=u.id, category_id=c.id, title='Lunch', amount=300.0, type='expense', date=today)
        db.session.add(t2)
        db.session.commit()
        self.assertEqual(b.status(), 'danger')
        self.assertEqual(b.get_raw_percentage(), 115.0)

    def test_auth_routes(self):
        # Register new account
        res = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'currency': '₹'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Login
        res_login = self.client.post('/auth/login', data={
            'login_id': 'newuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Welcome back, newuser!', res_login.data)

        # Logout
        res_logout = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertIn(b'logged out successfully', res_logout.data)

if __name__ == '__main__':
    unittest.main()
