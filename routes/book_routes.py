from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
from models import db, Book, Author, List, UserBook
from sqlalchemy import func, or_
from utils import map_book_data


bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.before_request
def check_auth():
    if not current_user.is_authenticated:
        abort(401)  # Unauthorized

@bp.route('/', methods=['GET'])
@login_required
def get_books():
    try:
        search_query = request.args.get('search', '')

        books_query = Book.query.join(UserBook).filter(
            UserBook.user_id == current_user.id, UserBook.is_read == True)

        if search_query:
            books_query = books_query.join(Author).filter(
                or_(Book.title.ilike(f'%{search_query}%'),
                    Author.name.ilike(f'%{search_query}%')))

        books = books_query.all()

        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'cover_image_url': book.cover_image_url
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error':
                        'An error occurred while fetching books'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_book(id):
    try:
        book = Book.query.get_or_404(id)
        book_data = map_book_data(book, current_user.id)

        book_data['lists'] = [{
            'id': list.id,
            'name': list.name
        } for list in book.lists if list.user_id == current_user.id or list.user_id is None]

        return jsonify(book_data)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_book: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching the book'}), 500

@bp.route('/<int:id>/read_status', methods=['PUT'])
@login_required
def update_read_status(id):
    try:
        data = request.get_json()
        is_read = data.get('is_read', False)

        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
        if user_book:
            user_book.is_read = is_read
        else:
            new_user_book = UserBook(user_id=current_user.id, book_id=id, is_read=is_read)
            db.session.add(new_user_book)

        db.session.commit()
        return jsonify({'message': 'Read status updated successfully', 'is_read': is_read})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating read status: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the read status'}), 500

@bp.route('/<int:id>/toggle_main_work', methods=['PUT'])
@login_required
def toggle_main_work(id):
    try:
        book = Book.query.get_or_404(id)
        
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized. Admin access required.'}), 403

        book.is_main_work = not book.is_main_work
        db.session.commit()
        return jsonify({'message': 'Main work status updated successfully', 'is_main_work': book.is_main_work})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating main work status: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the main work status'}), 500
