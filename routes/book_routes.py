from flask import Blueprint, jsonify, request
from app import db

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.route('/', methods=['GET'])
def get_books():
    Book = db.Model._decl_class_registry['Book']
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read
    } for book in books])

@bp.route('/<int:id>', methods=['GET'])
def get_book(id):
    Book = db.Model._decl_class_registry['Book']
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
    Book = db.Model._decl_class_registry['Book']
    Author = db.Model._decl_class_registry['Author']
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
    Book = db.Model._decl_class_registry['Book']
    book = Book.query.get_or_404(id)
    data = request.json
    book.is_read = data.get('is_read', book.is_read)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_book(id):
    Book = db.Model._decl_class_registry['Book']
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})

@bp.route('/author/<int:author_id>', methods=['GET'])
def get_books_by_author(author_id):
    Book = db.Model._decl_class_registry['Book']
    books = Book.query.filter_by(author_id=author_id).all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'is_read': book.is_read
    } for book in books])

@bp.route('/list/<int:list_id>', methods=['GET'])
def get_books_by_list(list_id):
    List = db.Model._decl_class_registry['List']
    list_ = List.query.get_or_404(list_id)
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'is_read': book.is_read
    } for book in list_.books])
