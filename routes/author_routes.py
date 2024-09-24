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
    current_app.logger.debug("get_authors function called")
    search_query = request.args.get('search', '')
    
    # Query for authors of books the user has read
    user_authors_query = Author.query.join(Book).filter(Book.users.any(id=current_user.id))
    
    # Query for all authors
    all_authors_query = Author.query
    
    if search_query:
        user_authors_query = user_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
        all_authors_query = all_authors_query.filter(func.lower(Author.name).contains(func.lower(search_query)))
    
    user_authors_query = user_authors_query.distinct()
    all_authors_query = all_authors_query.distinct()
    
    current_app.logger.debug(f"User Authors SQL Query: {user_authors_query}")
    current_app.logger.debug(f"All Authors SQL Query: {all_authors_query}")
    
    user_authors = user_authors_query.all()
    all_authors = all_authors_query.all()
    
    current_app.logger.debug(f"Raw user authors from database: {user_authors}")
    current_app.logger.debug(f"Raw all authors from database: {all_authors}")
    
    return jsonify({
        'all_authors': [{
            'id': author.id,
            'name': author.name,
            'book_count': len(author.books),
        } for author in all_authors],
        'user_authors': [{
            'id': author.id,
            'name': author.name,
            'book_count': sum(1 for book in author.books if any(user.id == current_user.id for user in book.users)),
            'read_percentage': calculate_read_percentage([book for book in author.books if any(user.id == current_user.id for user in book.users)])
        } for author in user_authors]
    })

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_author(id):
    current_app.logger.info(f"Fetching author with id: {id}")
    author = Author.query.get_or_404(id)
    current_app.logger.info(f"Author found: {author.name}")
    
    all_books = author.books
    user_books = [book for book in all_books if any(user.id == current_user.id for user in book.users)]
    
    books = []
    for book in all_books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        is_read = user_book.is_read if user_book else False
        current_app.logger.info(f"Book: {book.title}, is_read: {is_read}")
        books.append({
            'id': book.id,
            'title': book.title,
            'is_read': is_read
        })
    
    current_app.logger.info(f"Total number of books for author: {len(all_books)}")
    current_app.logger.info(f"Number of books read by user: {len([b for b in books if b['is_read']])}")
    
    read_percentage = calculate_read_percentage(user_books)
    current_app.logger.info(f"Read percentage: {read_percentage}")
    
    return jsonify({
        'id': author.id,
        'name': author.name,
        'books': books,
        'total_books': len(all_books),
        'read_books': len([b for b in books if b['is_read']]),
        'read_percentage': read_percentage
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
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

def calculate_read_percentage(books):
    if not books:
        return 0
    read_books = sum(1 for book in books if any(user.id == current_user.id for user in book.users))
    return (read_books / len(books)) * 100
