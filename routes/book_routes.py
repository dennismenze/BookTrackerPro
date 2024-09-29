from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook

bp = Blueprint('book', __name__)

@bp.route('/book/<int:id>')
@login_required
def book_detail(id):
    return render_template('book/detail.html', book_id=id)

@bp.route('/api/books')
@login_required
def api_books():
    books = Book.query.join(UserBook).filter(UserBook.user_id == current_user.id).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'cover_image_url': book.cover_image_url
    } for book in books])

# Add other book-related routes here
