from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, send_file, current_app, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, Author, List, UserBook, Post, Translation
from sqlalchemy import or_, func, and_, case, alias
from datetime import datetime, timedelta
from io import BytesIO, StringIO
from flask_babel import _, get_locale
import csv
import io
import logging
from utils import process_csv
import json

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    book_search_query = request.args.get('book_search', '')
    author_search_query = request.args.get('author_search', '')
    book_page = request.args.get('book_page', 1, type=int)
    author_page = request.args.get('author_page', 1, type=int)
    per_page = 10

    if current_user.is_authenticated:
        latest_books = Book.query.join(UserBook).filter(UserBook.user_id == current_user.id).order_by(UserBook.read_date.desc()).limit(5).all()
        
        user_authors = db.session.query(
            Author,
            func.count(Book.id).label('total_books'),
            func.sum(case((UserBook.read_date.isnot(None), 1), else_=0)).label('read_books'),
            func.count(case((Book.is_main_work == True, 1))).label('total_main_works'),
            func.sum(case((and_(UserBook.read_date.isnot(None), Book.is_main_work == True), 1), else_=0)).label('read_main_works')
        ).join(Book, Author.id == Book.author_id)\
         .outerjoin(UserBook, (UserBook.book_id == Book.id) & (UserBook.user_id == current_user.id))\
         .group_by(Author.id)\
         .order_by(func.sum(case((UserBook.read_date.isnot(None), 1), else_=0)).desc())\
         .limit(8)\
         .all()

        user_authors = [
            (author, total_books, read_books, total_main_works, read_main_works)
            for author, total_books, read_books, total_main_works, read_main_works in user_authors
            if total_books > 0 and read_books > 0
        ]

        for author, total_books, read_books, total_main_works, read_main_works in user_authors:
            author.read_percentage = (read_books / total_books * 100) if total_books > 0 else 0
            author.main_works_read_percentage = (read_main_works / total_main_works * 100) if total_main_works > 0 else 0
    else:
        latest_books = []
        user_authors = []

    books = None
    if book_search_query:
        books = Book.query.join(Translation, Book.title_id == Translation.id)\
            .join(Author, Book.author_id == Author.id)\
            .join(Translation.alias(), Author.name_id == Translation.id)\
            .filter(
                or_(
                    Translation.text_en.ilike(f'%{book_search_query}%'),
                    Translation.text_de.ilike(f'%{book_search_query}%')
                )
            ).paginate(page=book_page, per_page=per_page, error_out=False)

    authors = None
    if author_search_query:
        authors = Author.query.join(Translation, Author.name_id == Translation.id)\
            .filter(
                or_(
                    Translation.text_en.ilike(f'%{author_search_query}%'),
                    Translation.text_de.ilike(f'%{author_search_query}%')
                )
            ).paginate(page=author_page, per_page=per_page, error_out=False)

    return render_template('index.html',
                           latest_books=latest_books,
                           user_authors=user_authors,
                           books=books,
                           authors=authors,
                           book_search_query=book_search_query,
                           author_search_query=author_search_query)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash(_('Username already exists'))
            return redirect(url_for('home.register'))
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash(_('Email already exists'))
            return redirect(url_for('home.register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash(_('Registration successful. Please log in.'))
        return redirect(url_for('home.login'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home.index'))
        else:
            flash(_('Invalid username or password'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'))
    return redirect(url_for('home.index'))

@bp.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    recent_activities = []
    
    recent_books = UserBook.query.filter_by(user_id=user.id).filter(UserBook.read_date.isnot(None)).order_by(UserBook.read_date.desc()).limit(5).all()
    for user_book in recent_books:
        recent_activities.append({
            'type': 'book_read',
            'book': user_book.book,
            'timestamp': datetime.combine(user_book.read_date, datetime.min.time())
        })
    
    recent_lists = List.query.filter_by(user_id=user.id).order_by(List.id.desc()).limit(5).all()
    for list_item in recent_lists:
        recent_activities.append({
            'type': 'list_created',
            'list': list_item,
            'timestamp': datetime.fromtimestamp(list_item.id)
        })
    
    recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).limit(5).all()
    for post in recent_posts:
        recent_activities.append({
            'type': 'post_created',
            'post': post,
            'timestamp': post.timestamp
        })
    
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for activity in recent_activities:
        activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('profile.html', user=user, recent_activities=recent_activities[:15])

@bp.route('/profile_image/<int:user_id>')
def profile_image(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_image:
        return send_file(BytesIO(user.profile_image), mimetype='image/jpeg')
    else:
        return send_file('static/images/default-profile.png', mimetype='image/png')

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.bio = request.form.get('bio')
        current_user.location = request.form.get('location')
        current_user.website = request.form.get('website')
        
        profile_image = request.files.get('profile_image')
        if profile_image:
            current_user.profile_image = profile_image.read()
        
        db.session.commit()
        flash(_('Your profile has been updated.'))
        return redirect(url_for('home.user_profile', username=current_user.username))
    
    return render_template('edit_profile.html')

@bp.route('/set_language', methods=['POST'])
def set_language():
    language = request.form.get('language')
    if language and language in ['en', 'de', 'es', 'fr']:
        session['language'] = language
        if current_user.is_authenticated:
            current_user.preferred_language = language
            db.session.commit()
    return redirect(request.referrer or url_for('home.index'))

@bp.route('/import_csv', methods=['POST'])
@login_required
def import_csv():
    print("Received form data:", request.form)
    print("Received files:", request.files)

    csv_file = request.files.get('csv_file')
    if not csv_file:
        return jsonify({"error": "No CSV file provided"}), 400

    mappings_json = request.form.get('mappings')
    if not mappings_json:
        return jsonify({"error": "No mapping data provided"}), 400

    try:
        mappings = json.loads(mappings_json)
        print("Received mappings:", mappings)
    except json.JSONDecodeError:
        print("Error decoding JSON mappings")
        return jsonify({"error": "Invalid mapping data"}), 400

    csv_content = csv_file.read().decode('utf-8')
    csv_file = StringIO(csv_content)
    csv_reader = csv.DictReader(csv_file, delimiter=';')

    imported_books = 0
    for row in csv_reader:
        title = row[mappings['title']]
        author_name = row[mappings['author']]
        read_date_str = row[mappings['read_date']]

        if not title or not author_name:
            continue

        author = Author.query.filter(or_(
            Translation.text_en == author_name,
            Translation.text_de == author_name,
            Translation.text_en.ilike(f"%{author_name}%"),
            Translation.text_de.ilike(f"%{author_name}%")
        )).join(Author.name).first()

        if not author:
            print(f"Author not found: {author_name}")
            continue

        book = Book.query.filter(
            Book.author_id == author.id
        ).filter(or_(
            Translation.text_en == title,
            Translation.text_de == title,
            Translation.text_en.ilike(f"%{title}%"),
            Translation.text_de.ilike(f"%{title}%")
        )).join(Book.title).first()

        if not book:
            print(f"Book not found: {title} by {author_name}")
            continue

        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        if not user_book:
            user_book = UserBook(user_id=current_user.id, book_id=book.id)
            db.session.add(user_book)

            if read_date_str:
                try:
                    read_date = datetime.strptime(read_date_str, '%Y-%m-%d' if get_locale() == 'en' else '%d.%m.%Y')
                    user_book.read_date = read_date
                except ValueError:
                    print(f"Invalid date format for book: {title}")

            imported_books += 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(_("Database error occurred during import."))

    flash(_("CSV import processed successfully.") + " " + str(imported_books) + " " + _('books') + " " + _('imported'))
    return redirect(url_for('home.user_profile', username=current_user.username))

@bp.route('/export_csv')
@login_required
def export_csv():
    user_books = UserBook.query.filter_by(user_id=current_user.id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Title', 'Author', 'Read Date'])
    
    for user_book in user_books:
        writer.writerow([
            user_book.book.title.text_en,
            user_book.book.author.name.text_en,
            user_book.read_date.strftime('%Y-%m-%d') if user_book.read_date else ''
        ])
    
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=books_export.csv"}
    )