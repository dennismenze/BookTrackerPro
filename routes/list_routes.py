from flask import Blueprint, jsonify, request, current_app, session, abort
from flask_login import login_required, current_user
from models import db, Book, Author, List, UserBook
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_

bp = Blueprint('list', __name__, url_prefix='/api/lists')

@bp.before_request
def check_auth():
    current_app.logger.debug(f"check_auth called. Session: {session}")
    current_app.logger.debug(
        f"current_user.is_authenticated: {current_user.is_authenticated}")
    if not current_user.is_authenticated:
        current_app.logger.warning(
            f"User not authenticated. Session: {session}")
        abort(401)  # Unauthorized
    else:
        current_app.logger.debug(
            f"User authenticated. User ID: {current_user.id}")

@bp.route('/', methods=['GET'])
@login_required
def get_lists():
    try:
        search_query = request.args.get('search', '')
        if search_query:
            lists = List.query.filter(
                or_(List.user_id == current_user.id, List.user_id == None),
                func.lower(List.name).contains(
                    func.lower(search_query))).all()
        else:
            lists = List.query.filter(
                or_(List.user_id == current_user.id,
                    List.user_id == None)).all()
        return jsonify([{
            'id': list.id,
            'name': list.name,
            'book_count': len(list.books),
            'read_percentage': calculate_read_percentage(list.books, current_user.id),
            'is_public': list.is_public,
            'user_id': list.user_id
        } for list in lists])
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching lists: {str(e)}")
        return jsonify({'error':
                        'An error occurred while fetching lists'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_list(id):
    try:
        current_app.logger.info(f"Fetching list with id: {id}")
        list = List.query.filter(
            or_(List.id == id,
                List.user_id == current_user.id)).first_or_404()
        current_app.logger.info(f"List found: {list.name}")
        books = [{
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'author_id': book.author.id,
            'is_read': is_book_read(book, current_user.id),
            'cover_image_url': book.cover_image_url or '/static/images/no-cover.png'
        } for book in list.books]
        current_app.logger.info(f"Number of books in list: {len(books)}")
        read_percentage = calculate_read_percentage(list.books,
                                                    current_user.id)
        current_app.logger.info(f"Read percentage: {read_percentage}")
        return jsonify({
            'id': list.id,
            'name': list.name,
            'books': books,
            'read_percentage': read_percentage,
            'is_public': list.is_public
        })
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error fetching list details: {str(e)}")
        return jsonify(
            {'error': 'An error occurred while fetching list details'}), 500

@bp.route('/', methods=['POST'])
@login_required
def create_list():
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        is_public = data.get('is_public', False)
        user_id = None if is_public else current_user.id
        new_list = List(name=data['name'], user_id=user_id)
        db.session.add(new_list)
        db.session.commit()
        return jsonify({
            'id': new_list.id,
            'message': 'List created successfully'
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating list: {str(e)}")
        return jsonify({'error':
                        'An error occurred while creating the list'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_list(id):
    try:
        list = List.query.filter((List.id == id)
                                 & ((List.user_id == current_user.id)
                                    | (List.user_id == None))).first_or_404()

        data = request.get_json()
        if data and 'name' in data:
            list.name = data['name']

        if 'is_public' in data:
            if data['is_public']:
                list.user_id = None
            else:
                list.user_id = current_user.id

        db.session.commit()
        return jsonify({'message': 'List updated successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating list: {str(e)}")
        return jsonify({'error':
                        'An error occurred while updating the list'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_list(id):
    try:
        list = List.query.get_or_404(id)

        # Check if the user is an admin or the owner of the private list
        if current_user.is_admin or (list.user_id == current_user.id
                                     and not list.is_public):
            db.session.delete(list)
            db.session.commit()
            return jsonify({'message': 'List deleted successfully'})
        else:
            return jsonify({
                'error':
                'Unauthorized. You can only delete your own private lists.'
            }), 403
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting list: {str(e)}")
        return jsonify({'error':
                        'An error occurred while deleting the list'}), 500

@bp.route('/<int:id>/books', methods=['POST'])
@login_required
def add_book_to_list(id):
    try:
        list = List.query.filter(
            or_(List.id == id,
                List.user_id == current_user.id)).first_or_404()
        data = request.get_json()
        if not data or 'book_id' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        book = Book.query.filter(Book.id == data['book_id']).first_or_404()
        if book not in list.books:
            list.books.append(book)
            db.session.commit()
            return jsonify({'message': 'Book added to list successfully'})
        else:
            return jsonify({'message': 'Book already in list'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding book to list: {str(e)}")
        return jsonify(
            {'error':
             'An error occurred while adding the book to the list'}), 500

@bp.route('/<int:id>/books/<int:book_id>', methods=['DELETE'])
@login_required
def remove_book_from_list(id, book_id):
    try:
        list = List.query.filter(
            or_(List.id == id,
                List.user_id == current_user.id)).first_or_404()
        book = Book.query.filter_by(id=book_id).first_or_404()
        if book in list.books:
            list.books.remove(book)
            db.session.commit()
            return jsonify({'message': 'Book removed from list successfully'})
        return jsonify({'message': 'Book not in list'}), 404
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing book from list: {str(e)}")
        return jsonify({
            'error':
            'An error occurred while removing the book from the list'
        }), 500

def calculate_read_percentage(books, user_id):
    if not books:
        return 0
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    return (read_books / len(books)) * 100

def is_book_read(book, user_id):
    user_book = UserBook.query.filter_by(user_id=user_id,
                                         book_id=book.id).first()
    return user_book.is_read if user_book else False