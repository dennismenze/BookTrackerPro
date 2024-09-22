from flask import Blueprint, jsonify, request, current_app
from models import Author, Book

bp = Blueprint('author', __name__, url_prefix='/api/authors')

@bp.route('/', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{
        'id': author.id,
        'name': author.name,
        'book_count': len(author.books),
        'read_percentage': calculate_read_percentage(author.books)
    } for author in authors])

@bp.route('/<int:id>', methods=['GET'])
def get_author(id):
    current_app.logger.info(f"Fetching author with id: {id}")
    author = Author.query.get_or_404(id)
    current_app.logger.info(f"Author found: {author.name}")
    books = [{
        'id': book.id,
        'title': book.title,
        'is_read': book.is_read
    } for book in author.books]
    current_app.logger.info(f"Number of books for author: {len(books)}")
    read_percentage = calculate_read_percentage(author.books)
    current_app.logger.info(f"Read percentage: {read_percentage}")
    return jsonify({
        'id': author.id,
        'name': author.name,
        'books': books,
        'read_percentage': read_percentage
    })

@bp.route('/', methods=['POST'])
def create_author():
    data = request.json
    author = Author(name=data['name'])
    current_app.extensions['sqlalchemy'].db.session.add(author)
    current_app.extensions['sqlalchemy'].db.session.commit()
    return jsonify({
        'id': author.id,
        'message': 'Author created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get_or_404(id)
    data = request.json
    author.name = data.get('name', author.name)
    current_app.extensions['sqlalchemy'].db.session.commit()
    return jsonify({'message': 'Author updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get_or_404(id)
    current_app.extensions['sqlalchemy'].db.session.delete(author)
    current_app.extensions['sqlalchemy'].db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

def calculate_read_percentage(books):
    if not books:
        return 0
    read_books = sum(1 for book in books if book.is_read)
    return (read_books / len(books)) * 100
