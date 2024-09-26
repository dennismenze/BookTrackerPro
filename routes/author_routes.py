from flask import Blueprint, jsonify, request, current_app, abort
from flask_login import login_required, current_user
from models import db, Author, Book, UserBook
from sqlalchemy import func, or_

bp = Blueprint('author', __name__, url_prefix='/api/authors')

@bp.before_request
def check_auth():
    current_app.logger.debug(f"check_auth called. current_user.is_authenticated: {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        current_app.logger.warning(f"User not authenticated.")
        abort(401)  # Unauthorized
    else:
        current_app.logger.debug(f"User authenticated. User ID: {current_user.id}")

@bp.route('/', methods=['GET'])
@login_required
def get_authors():
    try:
        current_app.logger.debug(f"get_authors function called for user ID: {current_user.id}")
        search_query = request.args.get('search', '')
        
        user_authors_query = db.session.query(Author).join(Book).join(UserBook).filter(
            UserBook.user_id == current_user.id,
            UserBook.is_read == True
        ).distinct()
        
        all_authors_query = Author.query
        
        current_app.logger.debug(f"Initial user authors query: {user_authors_query}")
        current_app.logger.debug(f"Initial all authors query: {all_authors_query}")
        
        if search_query:
            user_authors_query = user_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
            all_authors_query = all_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
            current_app.logger.debug(f"User authors query after search filter: {user_authors_query}")
            current_app.logger.debug(f"All authors query after search filter: {all_authors_query}")
        
        user_authors = user_authors_query.all()
        all_authors = all_authors_query.all()
        
        current_app.logger.debug(f"Number of user authors found: {len(user_authors)}")
        current_app.logger.debug(f"Number of all authors found: {len(all_authors)}")
        
        result = {
            'all_authors': [{
                'id': author.id,
                'name': author.name,
                'book_count': len(author.books),
            } for author in all_authors],
            'user_authors': [{
                'id': author.id,
                'name': author.name,
                'book_count': sum(1 for book in author.books if any(user_book.user_id == current_user.id and user_book.is_read for user_book in book.user_books)),
                'read_percentage': calculate_read_percentage(author.books, current_user.id)
            } for author in user_authors]
        }
        
        current_app.logger.debug(f"Returning {len(result['all_authors'])} all authors and {len(result['user_authors'])} user authors")
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in get_authors: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching authors'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_author(id):
    current_app.logger.info(f"Fetching author with id: {id}")
    author = Author.query.get_or_404(id)
    current_app.logger.info(f"Author found: {author.name}")
    
    all_books = author.books
    user_books = [book for book in all_books if any(user.id == current_user.id for user in book.users)]
    
    books = []
    read_books_count = 0
    read_main_works_count = 0
    total_main_works_count = 0
    for book in all_books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        is_read = user_book.is_read if user_book else False
        if is_read:
            read_books_count += 1
            if book.is_main_work:
                read_main_works_count += 1
        if book.is_main_work:
            total_main_works_count += 1
        current_app.logger.info(f"Book: {book.title}, is_read: {is_read}, is_main_work: {book.is_main_work}")
        books.append({
            'id': book.id,
            'title': book.title,
            'is_read': is_read,
            'is_main_work': book.is_main_work
        })
    
    total_books = len(all_books)
    current_app.logger.info(f"Total number of books for author: {total_books}")
    current_app.logger.info(f"Number of books read by user: {read_books_count}")
    
    read_percentage = (read_books_count / total_books * 100) if total_books > 0 else 0
    read_main_works_percentage = (read_main_works_count / total_main_works_count * 100) if total_main_works_count > 0 else 0
    current_app.logger.info(f"Read percentage: {read_percentage}")
    current_app.logger.info(f"Read main works percentage: {read_main_works_percentage}")
    
    return jsonify({
        'id': author.id,
        'name': author.name,
        'books': books,
        'total_books': total_books,
        'read_books': read_books_count,
        'read_percentage': read_percentage,
        'total_main_works': total_main_works_count,
        'read_main_works': read_main_works_count,
        'read_main_works_percentage': read_main_works_percentage
    })

@bp.route('/', methods=['POST'])
@login_required
def create_author():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({
        'id': author.id,
        'message': 'Author created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_author(id):
    author = Author.query.get_or_404(id)
    data = request.get_json()
    if data and 'name' in data:
        author.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Author updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_author(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Admin access required.'}), 403
    
    author = Author.query.get_or_404(id)
    try:
        db.session.delete(author)
        db.session.commit()
        return jsonify({'message': 'Author deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting author: {str(e)}")
        return jsonify({'error': 'An error occurred while deleting the author'}), 500

def calculate_read_percentage(books, user_id):
    if not books:
        return 0
    read_books = sum(1 for book in books if any(user_book.user_id == user_id and user_book.is_read for user_book in book.user_books))
    return (read_books / len(books)) * 100