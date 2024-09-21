from flask import Blueprint, jsonify, request
from app import db
from models import Book, Author, List

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.route('/', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read
    } for book in books])

@bp.route('/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read,
        'lists': [list.name for list in book.lists]
    })

@bp.route('/', methods=['POST'])
def create_book():
    data = request.json
    author = Author.query.filter_by(name=data['author']).first()
    if not author:
        author = Author(name=data['author'])
        db.session.add(author)
    
    book = Book(title=data['title'], author=author, is_read=data.get('is_read', False))
    db.session.add(book)
    db.session.commit()
    return jsonify({'id': book.id, 'message': 'Book created successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.json
    book.is_read = data.get('is_read', book.is_read)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

@bp.route('/author/<int:author_id>', methods=['GET'])
def get_books_by_author(author_id):
    books = Book.query.filter_by(author_id=author_id).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'is_read': book.is_read
    } for book in books])

@bp.route('/list/<int:list_id>', methods=['GET'])
def get_books_by_list(list_id):
    list_ = List.query.get_or_404(list_id)
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read
    } for book in list_.books])
