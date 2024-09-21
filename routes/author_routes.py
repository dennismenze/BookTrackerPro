from flask import Blueprint, jsonify, request
from app import db

bp = Blueprint('author', __name__, url_prefix='/api/authors')

@bp.route('/', methods=['GET'])
def get_authors():
    Author = db.Model._decl_class_registry['Author']
    authors = Author.query.all()
    return jsonify([{
        'id': author.id,
        'name': author.name,
        'book_count': len(author.books),
        'read_percentage': calculate_read_percentage(author.books)
    } for author in authors])

@bp.route('/<int:id>', methods=['GET'])
def get_author(id):
    Author = db.Model._decl_class_registry['Author']
    author = Author.query.get_or_404(id)
    return jsonify({
        'id': author.id,
        'name': author.name,
        'books': [{
            'id': book.id,
            'title': book.title,
            'is_read': book.is_read
        } for book in author.books],
        'read_percentage': calculate_read_percentage(author.books)
    })

@bp.route('/', methods=['POST'])
def create_author():
    Author = db.Model._decl_class_registry['Author']
    data = request.json
    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({'id': author.id, 'message': 'Author created successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_author(id):
    Author = db.Model._decl_class_registry['Author']
    author = Author.query.get_or_404(id)
    data = request.json
    author.name = data.get('name', author.name)
    db.session.commit()
    return jsonify({'message': 'Author updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_author(id):
    Author = db.Model._decl_class_registry['Author']
    author = Author.query.get_or_404(id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})

def calculate_read_percentage(books):
    if not books:
        return 0
    read_books = sum(1 for book in books if book.is_read)
    return (read_books / len(books)) * 100
