from models import db, Author, Book, UserBook

def calculate_read_percentage(books, user_id):
    if not books:
        return 0
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    return (read_books / len(books)) * 100

def calculate_read_main_works_percentage(books, user_id):
    main_works = [book for book in books if book.is_main_work]
    if not main_works:
        return 0
    return calculate_read_percentage(main_works, user_id)

def get_books_stats(books, user_id):
    read_books = sum(1 for book in books if is_book_read(book, user_id))
    main_works = [book for book in books if book.is_main_work]
    read_main_works = sum(1 for book in main_works if is_book_read(book, user_id))
    return {
        'total_books': len(books),
        'read_books': read_books,
        'read_percentage': calculate_read_percentage(books, user_id),
        'total_main_works': len(main_works),
        'read_main_works': read_main_works,
        'read_main_works_percentage': calculate_read_main_works_percentage(books, user_id)
    }

def is_book_read(book, user_id):
    user_book = UserBook.query.filter_by(user_id=user_id,
                                         book_id=book.id).first()
    return user_book.is_read if user_book else False

def map_book_data(book, user_id):
    return {
        'id': book.id,
        'title': book.title,
        'author': book.author.name,
        'author_id': book.author_id,
        'is_read': is_book_read(book, user_id),
        'is_main_work': book.is_main_work,
        'cover_image_url': book.cover_image_url or '/static/images/no-cover.png'
    }