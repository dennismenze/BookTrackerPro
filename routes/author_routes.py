from flask import Blueprint, render_template, request, jsonify
from models import db, Author, Book, Translation, UserBook
from sqlalchemy.orm import joinedload
from flask_login import login_required, current_user
from flask_babel import _, get_locale
from datetime import date

bp = Blueprint('author', __name__)

@bp.route('/authors')
@login_required
def authors():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of authors per page
    search_query = request.args.get('search', '')

    query = Author.query.join(Translation, Author.name_id == Translation.id)

    if search_query:
        query = query.filter(Translation.text_en.ilike(f'%{search_query}%') | Translation.text_de.ilike(f'%{search_query}%'))

    authors = query.order_by(Translation.text_en).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('author/list.html',
                           authors=authors,
                           search_query=search_query)

@bp.route('/<int:id>')
@login_required
def author_detail(id):
    author = Author.query.get_or_404(id)
    books = Book.query.filter_by(author_id=author.id).all()
    
    # Calculate statistics for all books
    total_books = len(books)
    read_books = UserBook.query.filter(UserBook.book_id.in_([book.id for book in books]), 
                                       UserBook.user_id == current_user.id, 
                                       UserBook.read_date.isnot(None)).count()
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
    
    # Calculate statistics for main works
    main_works = [book for book in books if book.is_main_work]
    total_main_works = len(main_works)
    main_works_read = UserBook.query.filter(UserBook.book_id.in_([book.id for book in main_works]),
                                            UserBook.user_id == current_user.id,
                                            UserBook.read_date.isnot(None)).count()
    main_works_read_percentage = (main_works_read / total_main_works * 100) if total_main_works > 0 else 0
    
    # Add is_read status to books
    for book in books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        book.is_read = user_book.read_date is not None if user_book else False
    
    lang = str(get_locale())
    return render_template('author/detail.html', 
                           author=author, 
                           books=books, 
                           total_books=total_books, 
                           read_books=read_books, 
                           read_percentage=read_percentage,
                           total_main_works=total_main_works,
                           main_works_read=main_works_read,
                           main_works_read_percentage=main_works_read_percentage,
                           lang=lang)

@bp.route('/author/authors')
def api_authors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search_query = request.args.get('search', '')
    
    query = Author.query.join(Translation, Author.name_id == Translation.id)

    if search_query:
        query = query.filter(Translation.text_en.ilike(f'%{search_query}%') | Translation.text_de.ilike(f'%{search_query}%'))

    authors = query.order_by(Translation.text_en).paginate(page=page, per_page=per_page, error_out=False)
    
    lang = str(get_locale())
    return jsonify({
        'authors': [{
            'id': author.id,
            'name': author.name.text_en if lang == 'en' else author.name.text_de,
            'image_url': author.image_url
        } for author in authors.items],
        'total': authors.total,
        'pages': authors.pages,
        'current_page': authors.page
    })

@bp.route('/toggle_read_status', methods=['POST'])
@login_required
def toggle_read_status():
    data = request.json
    book_id = data.get('book_id')
    is_read = data.get('is_read')

    if book_id is None or is_read is None:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if user_book:
        user_book.read_date = date.today() if is_read else None
    else:
        user_book = UserBook(user_id=current_user.id, book_id=book_id, read_date=date.today() if is_read else None)
        db.session.add(user_book)

    db.session.commit()

    # Recalculate statistics
    author = Book.query.get(book_id).author
    books = Book.query.filter_by(author_id=author.id).all()
    total_books = len(books)
    read_books = UserBook.query.filter(UserBook.book_id.in_([book.id for book in books]), 
                                       UserBook.user_id == current_user.id, 
                                       UserBook.read_date.isnot(None)).count()
    read_percentage = (read_books / total_books * 100) if total_books > 0 else 0

    # Calculate statistics for main works
    main_works = [book for book in books if book.is_main_work]
    total_main_works = len(main_works)
    main_works_read = UserBook.query.filter(UserBook.book_id.in_([book.id for book in main_works]),
                                            UserBook.user_id == current_user.id,
                                            UserBook.read_date.isnot(None)).count()
    main_works_read_percentage = (main_works_read / total_main_works * 100) if total_main_works > 0 else 0

    return jsonify({
        'success': True,
        'read_books': read_books,
        'read_percentage': read_percentage,
        'main_works_read': main_works_read,
        'main_works_read_percentage': main_works_read_percentage
    })