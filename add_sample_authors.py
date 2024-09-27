from app import create_app, db
from models import Author

def add_sample_authors():
    app = create_app()
    with app.app_context():
        # Add 20 sample authors
        for i in range(1, 21):
            author = Author(name=f"Sample Author {i}")
            db.session.add(author)
        db.session.commit()
        print("20 sample authors have been added to the database.")

if __name__ == "__main__":
    add_sample_authors()
