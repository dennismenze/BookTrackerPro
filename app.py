import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Book, Author, List, UserBook
from functools import wraps
from sqlalchemy import func
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    db.init_app(app)
    migrate = Migrate(app, db)
    
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def before_request():
        g.user = current_user

    @app.route('/')
    def index():
        latest_books = []
        user_authors = []
        books = None
        authors = None

        if current_user.is_authenticated:
            latest_books = Book.query.join(UserBook).filter(
                UserBook.user_id == current_user.id).order_by(
                    Book.id.desc()).limit(5).all()
            user_authors = Author.query.join(Book).join(UserBook).filter(
                UserBook.user_id == current_user.id).distinct().all()

        book_search_query = request.args.get('book_search', '')
        author_search_query = request.args.get('author_search', '')

        if book_search_query:
            book_page = request.args.get('book_page', 1, type=int)
            book_per_page = 10
            book_query = Book.query.filter(
                Book.title.ilike(f'%{book_search_query}%'))
            books = book_query.paginate(page=book_page,
                                        per_page=book_per_page,
                                        error_out=False)

        if author_search_query:
            author_page = request.args.get('author_page', 1, type=int)
            author_per_page = 10
            authors_query = Author.query.filter(
                Author.name.ilike(f'%{author_search_query}%'))
            authors = authors_query.paginate(page=author_page,
                                             per_page=author_per_page,
                                             error_out=False)

        return render_template('index.html',
                               latest_books=latest_books,
                               user_authors=user_authors,
                               books=books,
                               book_search_query=book_search_query,
                               authors=authors,
                               author_search_query=author_search_query)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists')
            else:
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('index'))
        return render_template('register.html')

    @app.route('/authors')
    @login_required
    def authors():
        return render_template('authors.html')

    @app.route('/author/<int:id>')
    @login_required
    def author_detail(id):
        return render_template('author/detail.html', author_id=id)

    @app.route('/book/<int:id>')
    @login_required
    def book_detail(id):
        return render_template('book/detail.html', book_id=id)

    @app.route('/lists')
    @login_required
    def lists():
        return render_template('list/list.html',
                               user_id=current_user.id,
                               is_admin=current_user.is_admin)

    @app.route('/list/<int:id>')
    @login_required
    def list_detail(id):
        return render_template('list/detail.html', list_id=id)

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash('You do not have permission to access this page.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/admin')
    @login_required
    @admin_required
    def admin():
        return render_template('admin/dashboard.html')

    @app.route('/admin/users', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_users():
        if request.method == 'POST':
            action = request.form.get('action')
            user_id = request.form.get('user_id')

            if action == 'delete':
                user = db.session.get(User, user_id)
                if user:
                    try:
                        UserBook.query.filter_by(user_id=user.id).delete()

                        BookList = db.Table('book_list',
                                            db.metadata,
                                            autoload_with=db.engine)
                        books_to_remove = db.session.query(
                            Book.id).join(UserBook).filter(
                                UserBook.user_id == user.id).subquery()
                        db.session.execute(BookList.delete().where(
                            BookList.c.book_id.in_(books_to_remove)))

                        List.query.filter_by(user_id=user.id).update(
                            {'user_id': None})

                        Book.query.filter(Book.id.in_(books_to_remove)).delete(
                            synchronize_session=False)

                        db.session.delete(user)
                        db.session.commit()
                        flash('User and associated data deleted successfully.')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Error deleting user: {str(e)}")
                        flash(
                            'An error occurred while deleting the user. Please try again.'
                        )
                else:
                    flash('User not found.')

            elif action == 'toggle_admin':
                user = User.query.get(user_id)
                if user:
                    user.is_admin = not user.is_admin
                    db.session.commit()
                    flash(
                        f"Admin status for {user.username} has been {'granted' if user.is_admin else 'revoked'}."
                    )
                else:
                    flash('User not found.')

            return redirect(url_for('admin_users'))

        users = User.query.all()
        return render_template('admin/users.html', users=users)

    @app.route('/admin/books', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_books():
        if request.method == 'POST':
            action = request.form.get('action')
            book_id = request.form.get('book_id')

            if action == 'delete':
                book = Book.query.get(book_id)
                if book:
                    try:
                        book.lists = []

                        UserBook.query.filter_by(book_id=book.id).delete()

                        db.session.delete(book)
                        db.session.commit()
                        flash('Book deleted successfully.')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Error deleting book: {str(e)}")
                        flash(
                            'An error occurred while deleting the book. Please try again.'
                        )
                else:
                    flash('Book not found.')

            return redirect(url_for('admin_books'))

        books = Book.query.all()
        return render_template('admin/books.html', books=books)

    @app.route('/admin/authors', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_authors():
        if request.method == 'POST':
            action = request.form.get('action')
            if action == 'bulk_delete':
                author_ids = request.form.getlist('author_ids')
                if author_ids:
                    try:
                        for author_id in author_ids:
                            author = Author.query.get(author_id)
                            if author:
                                books = Book.query.filter_by(
                                    author_id=author.id).all()
                                for book in books:
                                    UserBook.query.filter_by(
                                        book_id=book.id).delete()
                                    db.session.delete(book)
                                db.session.delete(author)
                        db.session.commit()
                        flash(
                            f'{len(author_ids)} authors and their associated books have been deleted successfully.'
                        )
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(
                            f"Error bulk deleting authors: {str(e)}")
                        flash(
                            'An error occurred while deleting the authors. Please try again.'
                        )
                else:
                    flash('No authors selected for deletion.')
            return redirect(url_for('admin_authors'))

        page = request.args.get('page', 1, type=int)
        per_page = 10
        search_query = request.args.get('search', '')

        authors_query = Author.query

        if search_query:
            authors_query = authors_query.filter(
                Author.name.ilike(f'%{search_query}%'))

        authors = authors_query.paginate(page=page,
                                         per_page=per_page,
                                         error_out=False)
        return render_template('admin/authors.html',
                               authors=authors,
                               search_query=search_query)

    @app.route('/admin/authors/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_add_author():
        if request.method == 'POST':
            name = request.form.get('name')
            if name:
                new_author = Author(name=name)

                if 'image' in request.files:
                    file = request.files['image']
                    if file.filename != '':
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                 filename)
                        file.save(file_path)
                        new_author.image_url = url_for(
                            'static', filename=f'uploads/{filename}')

                db.session.add(new_author)
                db.session.commit()
                flash('Author added successfully.')
                return redirect(url_for('admin_authors'))
            else:
                flash('Author name is required.')
        return render_template('admin/author_form.html')

    @app.route('/admin/authors/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_edit_author(id):
        author = Author.query.get_or_404(id)
        if request.method == 'POST':
            name = request.form.get('name')
            if name:
                author.name = name

                if 'image' in request.files:
                    file = request.files['image']
                    if file.filename != '':
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                 filename)
                        file.save(file_path)
                        author.image_url = url_for(
                            'static', filename=f'uploads/{filename}')

                db.session.commit()
                flash('Author updated successfully.')
                return redirect(url_for('admin_authors'))
            else:
                flash('Author name is required.')
        return render_template('admin/author_form.html', author=author)

    @app.route('/admin/authors/<int:id>/delete', methods=['POST'])
    @login_required
    @admin_required
    def admin_delete_author(id):
        author = Author.query.get_or_404(id)
        try:
            books = Book.query.filter_by(author_id=author.id).all()
            for book in books:
                UserBook.query.filter_by(book_id=book.id).delete()
                db.session.delete(book)

            db.session.delete(author)
            db.session.commit()
            flash('Author and associated books deleted successfully.')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting author: {str(e)}")
            flash(
                'An error occurred while deleting the author. Please try again.'
            )
        return redirect(url_for('admin_authors'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
