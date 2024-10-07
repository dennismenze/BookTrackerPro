from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Author, db, List, Book, UserBook, BookList, Translation
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func
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

@bp.route('/<int:id>')
@login_required
def list_detail(id):
    book_list = List.query.get_or_404(id)

    if book_list.user_id != current_user.id and not book_list.is_public:
        flash('You do not have permission to view this list.', 'error')
        return redirect(url_for('list.lists'))

    sort_by = request.args.get('sort', 'rank')
    page = request.args.get('page', 1, type=int)
    per_page = 100  # Update to 100 books per page

    books_query = db.session.query(Book, BookList.rank, UserBook.read_date)\
        .join(BookList, Book.id == BookList.book_id)\
        .outerjoin(UserBook, (UserBook.book_id == Book.id) & (UserBook.user_id == current_user.id))\
        .filter(BookList.list_id == id)

    if sort_by == 'rank':
        books_query = books_query.order_by(BookList.rank)
    elif sort_by == 'title':
        books_query = books_query.order_by(Book.title)
    elif sort_by == 'author':
        books_query = books_query.join(Book.author).order_by(Author.name)
    elif sort_by == 'read_status':
        books_query = books_query.order_by(UserBook.read_date.desc().nullslast())

    paginated_books = books_query.paginate(page=page, per_page=per_page, error_out=False)

    books = []
    total_books = paginated_books.total
    read_books = 0
    total_main_works = 0
    main_works_read = 0
    for book, rank, read_date in paginated_books.items:
        is_read = read_date is not None
        if is_read:
            read_books += 1
        if book.is_main_work:
            total_main_works += 1
            if is_read:
                main_works_read += 1
        books.append({
            'id': book.id,
            'title': book.title,
            'author': book.author.name,
            'author_id': book.author_id,
            'cover_image_url': book.cover_image_url,
            'is_read': is_read,
            'rank': "" if rank == 0 else str(rank) +("th" if 4<=rank%100<=20 else {1:"st",2:"nd",3:"rd"}.get(rank%10, "th")),
            'is_main_work': book.is_main_work
        })

    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    main_works_read_percentage = (main_works_read / total_main_works * 100) if total_main_works > 0 else 0

    return render_template('list/detail.html',
                           list=book_list,
                           books=books,
                           pagination=paginated_books,
                           read_percentage=read_percentage,
                           sort_by=sort_by,
                           total_main_works=total_main_works,
                           main_works_read=main_works_read,
                           main_works_read_percentage=main_works_read_percentage)

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    list_id = data.get('list_id')
    is_read = data.get('is_read')

    if book_id is None or list_id is None or is_read is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.read_date = date.today() if is_read else None
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, read_date=date.today() if is_read else None)
        db.session.add(user_book)

    db.session.commit()

    book_list = List.query.get(list_id)
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
        'read_percentage': round(read_percentage, 0),
        'main_works_read': main_works_read,
        'main_works_read_percentage': round(main_works_read_percentage, 0)
    })

@bp.route('/search_books', methods=['GET'])
@login_required
def search_books():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    books = Book.query.filter(
        or_(Book.title.ilike(f'%{query}%'),
            Book.author.has(name=query))).limit(10).all()

    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'cover_image_url': book.cover_image_url
    } for book in books])

@bp.route('/add_book_to_list', methods=['POST'])
@login_required
def add_book_to_list():
    data = request.json
    book_id = data.get('book_id')
    list_id = data.get('list_id')

    if not book_id or not list_id:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    book_list = List.query.get(list_id)
    if not book_list or book_list.user_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'List not found or access denied'
        }), 404

    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    existing_book_list = BookList.query.filter_by(list_id=list_id,
                                                  book_id=book_id).first()
    if existing_book_list:
        return jsonify({
            'success': False,
            'error': 'Book already in list'
        }), 400

    max_rank = db.session.query(func.max(
        BookList.rank)).filter_by(list_id=list_id).scalar() or 0
    new_book_list = BookList(list_id=list_id,
                             book_id=book_id,
                             rank=max_rank + 1)
    db.session.add(new_book_list)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Book added to list'})

@bp.route('/remove_book_from_list', methods=['POST'])
@login_required
def remove_book_from_list():
    data = request.json
    book_id = data.get('book_id')
    list_id = data.get('list_id')

    if not book_id or not list_id:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    book_list = List.query.get(list_id)
    if not book_list or book_list.user_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'List not found or access denied'
        }), 404

    book_list_entry = BookList.query.filter_by(list_id=list_id,
                                               book_id=book_id).first()
    if not book_list_entry:
        return jsonify({'success': False, 'error': 'Book not in list'}), 400

    db.session.delete(book_list_entry)
    db.session.commit()

    remaining_books = BookList.query.filter_by(list_id=list_id).order_by(
        BookList.rank).all()
    for i, book in enumerate(remaining_books, start=1):
        book.rank = i
    db.session.commit()

    return jsonify({'success': True, 'message': 'Book removed from list'})

@bp.route('/update_ranks', methods=['POST'])
@login_required
def update_ranks():
    data = request.json
    list_id = data.get('list_id')
    book_ids = data.get('book_ids')

    if not list_id or not book_ids:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    book_list = List.query.get(list_id)
    if not book_list or book_list.user_id != current_user.id:
        return jsonify({
            'success': False,
            'error': 'List not found or access denied'
        }), 404

    try:
        for index, book_id in enumerate(book_ids, start=1):
            book_list_entry = BookList.query.filter_by(
                list_id=list_id, book_id=book_id).first()
            if book_list_entry:
                book_list_entry.rank = index
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Ranks updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/toggle_visibility', methods=['POST'])
@login_required
def toggle_visibility():
    data = request.json
    list_id = data.get('list_id')
    is_public = data.get('is_public')

    if list_id is None or is_public is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    book_list = List.query.get(list_id)
    if not book_list or (not book_list.is_public
                         and book_list.user_id != current_user.id):
        return jsonify({
            'success': False,
            'error': 'List not found or access denied'
        }), 404

    book_list.is_public = is_public
    db.session.commit()

    return jsonify({'success': True, 'is_public': book_list.is_public})