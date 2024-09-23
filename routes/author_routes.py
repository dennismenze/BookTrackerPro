from flask import Blueprint, jsonify, request, current_app, session, abort
from flask_login import login_required, current_user
from models import db, Author, Book

bp = Blueprint('author', __name__, url_prefix='/api/authors')

@bp.before_request
def check_auth():
    if 'user_id' not in session:
        abort(401)  # Unauthorized

@bp.route('/', methods=['GET'])
@login_required
def get_authors():
    authors = Author.query.join(Book).filter(Book.user_id == current_user.id).distinct().all()
    return jsonify([{
        'id': author.id,
        'name': author.name,
        'book_count': len([book for book in author.books if book.user_id == current_user.id]),
        'read_percentage': calculate_read_percentage([book for book in author.books if book.user_id == current_user.id])
    } for author in authors])

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_author(id):
    current_app.logger.info(f"Fetching author with id: {id}")
    author = Author.query.get_or_404(id)
    current_app.logger.info(f"Author found: {author.name}")
    books = [{
        'id': book.id,
        'title': book.title,
        'is_read': book.is_read
    } for book in author.books if book.user_id == current_user.id]
    current_app.logger.info(f"Number of books for author: {len(books)}")
    read_percentage = calculate_read_percentage([book for book in author.books if book.user_id == current_user.id])
    current_app.logger.info(f"Read percentage: {read_percentage}")
    return jsonify({
        'id': author.id,
        'name': author.name,
        'books': books,
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
    read_books = sum(1 for book in books if book.is_read)
    return (read_books / len(books)) * 100
