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
    book = Book.query.options(joinedload(Book.user_books)).get_or_404(id)
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    is_read = user_book.read_date is not None if user_book else False
    read_date = user_book.read_date if user_book else None
    user_rating = user_book.rating if user_book and user_book.rating is not None else 0
    user_review = user_book.review if user_book else None

    reviews = UserBook.query.filter_by(book_id=book.id).filter(UserBook.review.isnot(None)).all()

    lang = str(get_locale())
    return render_template('book/detail.html',
                           book=book,
                           is_read=is_read,
                           read_date=read_date,
                           user_rating=user_rating,
                           user_review=user_review,
                           reviews=reviews,
                           lang=lang,
                           _l=_)

@bp.route('/<int:id>/lists')
@login_required
def book_lists(id):
    book = Book.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    query = List.query.filter(List.books.any(id=book.id))

    if sort == 'name':
        query = query.order_by(List.name.asc() if order == 'asc' else List.name.desc())
    elif sort == 'visibility':
        query = query.order_by(List.is_public.asc() if order == 'asc' else List.is_public.desc())

    lists = query.paginate(page=page, per_page=per_page, error_out=False)

    lang = str(get_locale())
    return jsonify({
        'lists': [{
            'id': list.id,
            'name': list.name.text_de if lang == 'de' else list.name.text_en,
            'is_public': list.is_public
        } for list in lists.items],
        'total': lists.total,
        'pages': lists.pages,
        'current_page': lists.page
    })

@bp.route('/books')
@login_required
def api_books():
    books = Book.query.join(UserBook).filter(
        UserBook.user_id == current_user.id).all()
    lang = str(get_locale())
    return jsonify([{
        'id': book.id,
        'title': book.title.text_de if lang == 'de' else book.title.text_en,
        'author': book.author.name.text_de if lang == 'de' else book.author.name.text_en,
        'cover_image_url': book.cover_image_url
    } for book in books])

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

    return jsonify({'success': True, 'is_read': is_read, 'read_date': user_book.read_date.isoformat() if user_book.read_date else None})

@bp.route('/rate', methods=['POST'])
@login_required
def rate_book():
    data = request.json
    book_id = data.get('book_id')
    rating = data.get('rating')

    if book_id is None or rating is None:
        return jsonify({'success': False, 'error': _('Invalid data')}), 400

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

    return jsonify({'success': True, 'review': review})