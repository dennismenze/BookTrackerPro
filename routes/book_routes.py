from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook, Author

bp = Blueprint('book', __name__)

@bp.route('/<int:id>')
@login_required
def book_detail(id):
    return render_template('book/detail.html', book_id=id)

@bp.route('/api/books')
@login_required
def api_books():
    print("API books route hit")  # Debug print statement
    books = Book.query.join(UserBook).filter(UserBook.user_id == current_user.id).all()
    print(f"Number of books: {len(books)}")  # Debug print statement
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'cover_image_url': book.cover_image_url
    } for book in books])

@bp.route('/api/book/<int:id>')
@login_required
def api_book_detail(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'cover_image_url': book.cover_image_url,
        'isbn': book.isbn,
        'description': book.description,
        'page_count': book.page_count,
        'published_date': book.published_date
    })

# Add other book-related routes here
