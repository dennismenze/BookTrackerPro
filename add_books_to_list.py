from app import create_app
from models import db, List, Book, UserBook
from flask_login import current_user

def add_books_to_test_list():
    app = create_app()
    with app.app_context():
        # Find the "Test" list
        test_list = List.query.filter_by(name="Test").first()
        
        if test_list:
            # Add some books to the list
            books = Book.query.limit(4).all()
            for book in books:
                if book not in test_list.books:
                    test_list.books.append(book)
            
            db.session.commit()
            print(f"Added {len(books)} books to the 'Test' list")
        else:
            print("'Test' list not found")

if __name__ == "__main__":
    add_books_to_test_list()
