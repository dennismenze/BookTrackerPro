from flask import Blueprint, jsonify, request
from app import db
from models import Book, Author, List

bp = Blueprint('list', __name__, url_prefix='/api/lists')


@bp.route('/', methods=['GET'])
def get_lists():
    lists = List.query.all()
    return jsonify([{
        'id': list.id,
        'name': list.name,
        'book_count': len(list.books),
        'read_percentage': calculate_read_percentage(list.books)
    } for list in lists])


@bp.route('/<int:id>', methods=['GET'])
def get_list(id):
    list = List.query.get_or_404(id)
    return jsonify({
        'id':
        list.id,
        'name':
        list.name,
        'books': [{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'is_read': book.is_read
        } for book in list.books],
        'read_percentage':
        calculate_read_percentage(list.books)
    })


@bp.route('/', methods=['POST'])
def create_list():
    data = request.json
    new_list = List(name=data['name'])
    db.session.add(new_list)
    db.session.commit()
    return jsonify({
        'id': new_list.id,
        'message': 'List created successfully'
    }), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_list(id):
    list = List.query.get_or_404(id)
    data = request.json
    list.name = data.get('name', list.name)
    db.session.commit()
    return jsonify({'message': 'List updated successfully'})


@bp.route('/<int:id>', methods=['DELETE'])
def delete_list(id):
    list = List.query.get_or_404(id)
    db.session.delete(list)
    db.session.commit()
    return jsonify({'message': 'List deleted successfully'})


@bp.route('/<int:id>/books', methods=['POST'])
def add_book_to_list(id):
    list = List.query.get_or_404(id)
    data = request.json
    book = Book.query.get_or_404(data['book_id'])
    list.books.append(book)
    db.session.commit()
    return jsonify({'message': 'Book added to list successfully'})


@bp.route('/<int:id>/books/<int:book_id>', methods=['DELETE'])
def remove_book_from_list(id, book_id):
    list = List.query.get_or_404(id)
    book = Book.query.get_or_404(book_id)
    if book in list.books:
        list.books.remove(book)
        db.session.commit()
        return jsonify({'message': 'Book removed from list successfully'})
    return jsonify({'message': 'Book not in list'}), 404


def calculate_read_percentage(books):
    if not books:
        return 0
    read_books = sum(1 for book in books if book.is_read)
    return (read_books / len(books)) * 100
