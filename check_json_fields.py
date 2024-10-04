from app import app, db
from models import Book, Author, List, Post
import json

def check_and_update_json_fields():
    with app.app_context():
        # Check and update Book model
        books = Book.query.all()
        for book in books:
            if not isinstance(book.title, dict):
                try:
                    book.title = json.loads(book.title)
                except json.JSONDecodeError:
                    book.title = {"en": book.title}
            
            if book.description and not isinstance(book.description, dict):
                try:
                    book.description = json.loads(book.description)
                except json.JSONDecodeError:
                    book.description = {"en": book.description}

        # Check and update Author model
        authors = Author.query.all()
        for author in authors:
            if not isinstance(author.name, dict):
                try:
                    author.name = json.loads(author.name)
                except json.JSONDecodeError:
                    author.name = {"en": author.name}
            
            if author.bio and not isinstance(author.bio, dict):
                try:
                    author.bio = json.loads(author.bio)
                except json.JSONDecodeError:
                    author.bio = {"en": author.bio}

        # Check and update List model
        lists = List.query.all()
        for list_item in lists:
            if not isinstance(list_item.name, dict):
                try:
                    list_item.name = json.loads(list_item.name)
                except json.JSONDecodeError:
                    list_item.name = {"en": list_item.name}
            
            if list_item.description and not isinstance(list_item.description, dict):
                try:
                    list_item.description = json.loads(list_item.description)
                except json.JSONDecodeError:
                    list_item.description = {"en": list_item.description}

        # Check and update Post model
        posts = Post.query.all()
        for post in posts:
            if post.body and not isinstance(post.body, dict):
                try:
                    post.body = json.loads(post.body)
                except json.JSONDecodeError:
                    post.body = {"en": post.body}

        # Commit all changes
        db.session.commit()
        print("JSON fields have been checked and updated.")

if __name__ == "__main__":
    check_and_update_json_fields()
