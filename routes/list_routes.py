from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, List, Book, UserBook, BookList, Translation
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func, and_
from datetime import date
from flask_babel import _, get_locale

bp = Blueprint('list', __name__)

@bp.route('/lists')
@login_required
def lists():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '')

    query = List.query.join(Translation, List.name_id == Translation.id).filter(
        or_(List.user_id == current_user.id, List.is_public == True)
    )

    if search_query:
        query = query.filter(or_(
            Translation.text_en.ilike(f'%{search_query}%'),
            Translation.text_de.ilike(f'%{search_query}%')
        ))

    lists = query.order_by(Translation.text_en).paginate(page=page, per_page=per_page, error_out=False)

    for list_item in lists.items:
        list_item.preview_books = list_item.books[:5]
        list_item.book_count = len(list_item.books)

    lang = str(get_locale())
    return render_template('list/list.html',
                           lists=lists,
                           search_query=search_query,
                           lang=lang)

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    list_id = data.get('list_id')
    is_read = data.get('is_read')

    if book_id is None or list_id is None or is_read is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    try:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

        if user_book:
            user_book.read_date = date.today() if is_read else None
        else:
            user_book = UserBook(user_id=current_user.id, book_id=book_id, read_date=date.today() if is_read else None)
            db.session.add(user_book)

        db.session.commit()

        book_list = List.query.get(list_id)
        if not book_list:
            return jsonify({'success': False, 'error': 'List not found'}), 404

        total_books = len(book_list.books)
        read_books = UserBook.query.filter(
            UserBook.user_id == current_user.id,
            UserBook.book_id.in_([book.id for book in book_list.books]),
            UserBook.read_date.isnot(None)).count()
        read_percentage = (read_books / total_books * 100) if total_books > 0 else 0

        main_works = [book for book in book_list.books if book.is_main_work]
        total_main_works = len(main_works)
        main_works_read = UserBook.query.filter(
            UserBook.user_id == current_user.id,
            UserBook.book_id.in_([book.id for book in main_works]),
            UserBook.read_date.isnot(None)).count()
        main_works_read_percentage = (main_works_read / total_main_works * 100) if total_main_works > 0 else 0

        return jsonify({
            'success': True,
            'is_read': is_read,
            'read_books': read_books,
            'total_books': total_books,
            'read_percentage': round(read_percentage, 1),
            'main_works_read': main_works_read,
            'total_main_works': total_main_works,
            'main_works_read_percentage': round(main_works_read_percentage, 1)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Add other route handlers here...
