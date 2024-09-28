from app import create_app, db
from models import User

def create_test_user():
    app = create_app()
    with app.app_context():
        # Check if the test user already exists
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            # Create a new test user
            test_user = User(username='testuser', email='testuser@example.com')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully.")
        else:
            print("Test user already exists.")

if __name__ == '__main__':
    create_test_user()
