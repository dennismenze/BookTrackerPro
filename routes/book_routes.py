from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook, Author, List, BookList, Translation
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from datetime import date
from flask_babel import _, get_locale

bp = Blueprint('book', __name__)

@bp.route('/<int:id>')
@login_required
def book_detail(id):
    book = Book.query.get_or_404(id)
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
    is_read = user_book is not None and user_book.read_date is not None
    read_date = user_book.read_date if user_book else None
    user_rating = user_book.rating if user_book else None
    user_review = user_book.review if user_book else ""
    reviews = UserBook.query.filter(UserBook.book_id == id, UserBook.review != None).all()
    
    return render_template('book/detail.html', 
                           book=book, 
                           is_read=is_read, 
                           read_date=read_date,
                           user_rating=user_rating,
                           user_review=user_review,
                           reviews=reviews)

@bp.route('/rate', methods=['POST'])
@login_required
def rate_book():
    data = request.json
    book_id = data.get('book_id')
    rating = data.get('rating')

    if book_id is None or rating is None:
        return jsonify({'success': False, 'error': _('Invalid data')}), 400

    # Convert rating to float
    try:
        rating = float(rating)
        if rating < 0 or rating > 5 or (rating * 2) % 1 != 0:  # Ensure rating is between 0 and 5, and is a multiple of 0.5
            raise ValueError
    except ValueError:
        return jsonify({'success': False, 'error': _('Invalid rating value')}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id,
                                         book_id=book_id).first()

    if user_book:
        user_book.rating = rating
    else:
        user_book = UserBook(user_id=current_user.id,
                             book_id=book_id,
                             rating=rating)
        db.session.add(user_book)

    db.session.commit()

    book = Book.query.get(book_id)
    return jsonify({
        'success': True,
        'rating': rating,
        'average_rating': book.average_rating
    })

@bp.route('/delete_rating', methods=['POST'])
@login_required
def delete_rating():
    data = request.json
    book_id = data.get('book_id')

    if book_id is None:
        return jsonify({'success': False, 'error': _('Invalid data')}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.rating = None
        db.session.commit()
        book = Book.query.get(book_id)
        return jsonify({
            'success': True,
            'message': _('Rating deleted successfully'),
            'average_rating': book.average_rating
        })
    else:
        return jsonify({'success': False, 'error': _('No rating found for this book')}), 404

@bp.route('/review', methods=['POST'])
@login_required
def review_book():
    data = request.json
    book_id = data.get('book_id')
    review = data.get('review')

    if book_id is None or review is None:
        return jsonify({'success': False, 'error': _('Invalid data')}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id,
                                         book_id=book_id).first()

    if user_book:
        user_book.review = review
    else:
        user_book = UserBook(user_id=current_user.id,
                             book_id=book_id,
                             review=review)
        db.session.add(user_book)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': _('Review submitted successfully')
    })

@bp.route('/<int:book_id>/lists')
@login_required
def book_lists(book_id):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    query = List.query.join(BookList).filter(BookList.book_id == book_id)

    if sort == 'name':
        query = query.order_by(List.name.asc() if order == 'asc' else List.name.desc())
    elif sort == 'visibility':
        query = query.order_by(List.is_public.asc() if order == 'asc' else List.is_public.desc())

    lists = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'lists': [{'id': l.id, 'name': l.name, 'is_public': l.is_public} for l in lists.items],
        'current_page': lists.page,
        'pages': lists.pages,
        'total': lists.total
    })

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    is_read = data.get('is_read')

    if book_id is None or is_read is None:
        return jsonify({'success': False, 'error': _('Invalid data')}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.read_date = date.today() if is_read else None
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, read_date=date.today() if is_read else None)
        db.session.add(user_book)

    db.session.commit()

    return jsonify({
        'success': True,
        'read_date': user_book.read_date.isoformat() if user_book.read_date else None
    })
