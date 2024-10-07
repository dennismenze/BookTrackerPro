from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Book, UserBook, Author, List, Translation
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
    user_rating = user_book.rating if user_book else 0
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

# ... [other routes remain unchanged]
