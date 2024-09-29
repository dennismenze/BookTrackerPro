from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook, Author, List

bp = Blueprint('book', __name__)

@bp.route('/<int:id>')
@login_required
def book_detail(id):
    book = Book.query.get_or_404(id)
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    book_in_list = user_book is not None
    is_read = user_book.is_read if user_book else False
    
    # Fetch all lists containing the book
    lists_containing_book = List.query.filter(List.books.any(id=book.id)).all()
    
    return render_template('book_detail.html', book=book, book_in_list=book_in_list, is_read=is_read, lists_containing_book=lists_containing_book)

@bp.route('/books')
@login_required
def api_books():
    books = Book.query.join(UserBook).filter(UserBook.user_id == current_user.id).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'cover_image_url': book.cover_image_url
    } for book in books])

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    is_read = data.get('is_read')

    if book_id is None or is_read is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.is_read = is_read
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, is_read=is_read)
        db.session.add(user_book)

    db.session.commit()

    return jsonify({
        'success': True,
        'is_read': is_read
    })

# Add other book-related routes here
