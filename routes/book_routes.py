from flask import Blueprint, jsonify, request, current_app
from models import db, Book, Author, List
import logging

bp = Blueprint('book', __name__, url_prefix='/api/books')

@bp.route('/', methods=['GET'])
def get_books():
    try:
        current_app.logger.debug(f"Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
        books = Book.query.all()
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'is_read': book.is_read
        } for book in books])
    except Exception as e:
        current_app.logger.error(f"Error in get_books: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching books'}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': book.is_read,
        'lists': [{'id': list.id, 'name': list.name} for list in book.lists]
    })

@bp.route('/', methods=['POST'])
def create_book():
    data = request.json
    author = Author.query.filter_by(name=data['author']).first()
    if not author:
        author = Author(name=data['author'])
        db.session.add(author)
    existing_book = Book.query.filter_by(title=data['title'], author=author).first()
    if existing_book:
        return jsonify({
            'id': existing_book.id,
            'message': 'Book already exists'
        }), 200
    book = Book(title=data['title'], author=author)
    db.session.add(book)
    db.session.commit()
    return jsonify({
        'id': book.id,
        'message': 'Book created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.json
    book.title = data.get('title', book.title)
    book.is_read = data.get('is_read', book.is_read)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})
