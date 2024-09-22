from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models import db, Book, Author, List

bp = Blueprint('list', __name__, url_prefix='/api/lists')

@bp.route('/', methods=['GET'])
@login_required
def get_lists():
    lists = List.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': list.id,
        'name': list.name,
        'book_count': len(list.books),
        'read_percentage': calculate_read_percentage(list.books)
    } for list in lists])

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_list(id):
    current_app.logger.info(f"Fetching list with id: {id}")
    list = List.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    current_app.logger.info(f"List found: {list.name}")
    books = [{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author.id,
        'is_read': book.is_read
    } for book in list.books]
    current_app.logger.info(f"Number of books in list: {len(books)}")
    read_percentage = calculate_read_percentage(list.books)
    current_app.logger.info(f"Read percentage: {read_percentage}")
    return jsonify({
        'id': list.id,
        'name': list.name,
        'books': books,
        'read_percentage': read_percentage
    })

@bp.route('/', methods=['POST'])
@login_required
def create_list():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    new_list = List()
    new_list.name = data['name']
    new_list.user_id = current_user.id
    db.session.add(new_list)
    db.session.commit()
    return jsonify({
        'id': new_list.id,
        'message': 'List created successfully'
    }), 201

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_list(id):
    list = List.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    if data and 'name' in data:
        list.name = data['name']
    db.session.commit()
    return jsonify({'message': 'List updated successfully'})

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_list(id):
    list = List.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(list)
    db.session.commit()
    return jsonify({'message': 'List deleted successfully'})

@bp.route('/<int:id>/books', methods=['POST'])
@login_required
def add_book_to_list(id):
    list = List.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    if not data or 'book_id' not in data:
        return jsonify({'error': 'Invalid request data'}), 400

    book = Book.query.filter_by(id=data['book_id'], user_id=current_user.id).first_or_404()
    list.books.append(book)
    db.session.commit()
    return jsonify({'message': 'Book added to list successfully'})

@bp.route('/<int:id>/books/<int:book_id>', methods=['DELETE'])
@login_required
def remove_book_from_list(id, book_id):
    list = List.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
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
