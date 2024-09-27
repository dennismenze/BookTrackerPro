import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, g
from models import db, Book, Author, List, User, UserBook
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from sqlalchemy import text, true, select, or_
from flask_migrate import Migrate
from flask_talisman import Talisman
from urllib.parse import urlparse
from functools import wraps

def create_app():
    app = Flask(__name__)

    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY",
                                              "fallback_secret_key")
    app.logger.debug(f"SECRET_KEY: {app.config['SECRET_KEY'][:5]}...")

    db.init_app(app)

    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    csp = {
        'default-src':
        "'self'",
        'script-src': [
            "'self'", "https://cdn.jsdelivr.net",
            "https://cdn.tailwindcss.com", "https://cdnjs.cloudflare.com",
            "'unsafe-inline'"  # Added 'unsafe-inline' to allow inline scripts
        ],
        'style-src': [
            "'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'",
            "https://cdnjs.cloudflare.com"
        ],
        'img-src': ["'self'", "https:", "data:"],
        'font-src': ["'self'", "https:", "data:"],
        'connect-src':
        "'self'",
        'upgrade-insecure-requests':
        ''
    }

    Talisman(app, content_security_policy=csp, force_https=True)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.logger.debug(
        f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    from routes import book_routes, author_routes, list_routes
    app.register_blueprint(book_routes.bp)
    app.register_blueprint(author_routes.bp)
    app.register_blueprint(list_routes.bp)

    @app.before_request
    def before_request():
        g.user = current_user

    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request path: {request.path}")

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        app.logger.debug("Register route accessed")
        if current_user.is_authenticated:
            app.logger.debug(
                "Authenticated user accessing register page, redirecting to index"
            )
            return redirect(url_for('index'))
        if request.method == 'POST':
            app.logger.debug("Processing POST request for registration")
            try:
                username = request.form['username']
                email = request.form['email']
                password = request.form['password']

                user = User.query.filter_by(username=username).first()
                if user:
                    app.logger.warning(
                        f"Registration attempt with existing username: {username}"
                    )
                    flash('Username already exists')
                    return redirect(url_for('register'))

                user = User.query.filter_by(email=email).first()
                if user:
                    app.logger.warning(
                        f"Registration attempt with existing email: {email}")
                    flash('Email already exists')
                    return redirect(url_for('register'))

                new_user = User(username=username, email=email)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()

                app.logger.info(
                    f"New user registered successfully: {username}")
                flash('Registration successful')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error during registration: {str(e)}')
                flash(
                    'An error occurred during registration. Please try again.')

        app.logger.debug("Rendering registration template")
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        app.logger.debug("Login route accessed")
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            try:
                username = request.form['username']
                password = request.form['password']
                app.logger.debug(
                    f"Processing POST request for login: {username}")
                user = User.query.filter_by(username=username).first()
                app.logger.debug(f"User found: {user}")
                if user:
                    if user.check_password(password):
                        login_user(user)
                        session['user_id'] = user.id
                        next_page = request.args.get('next')
                        if not next_page or urlparse(next_page).netloc != '':
                            next_page = url_for('index')
                        return redirect(next_page)
                    else:
                        flash('Invalid username or password')
                else:
                    flash('Invalid username or password')
            except Exception as e:
                flash('An error occurred during login. Please try again.')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        return redirect(url_for('index'))

    @app.route('/authors')
    @login_required
    def authors():
        return render_template('author/list.html',
                               user_id=current_user.id,
                               is_admin=current_user.is_admin)

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
                        Author.query.filter(Author.id.in_(author_ids)).delete(synchronize_session=False)
                        db.session.commit()
                        flash(f'{len(author_ids)} authors have been deleted successfully.')
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Error bulk deleting authors: {str(e)}")
                        flash('An error occurred while deleting the authors. Please try again.')
                else:
                    flash('No authors selected for deletion.')
            return redirect(url_for('admin_authors'))

        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of authors per page
        search_query = request.args.get('search', '')
        
        authors_query = Author.query
        
        if search_query:
            authors_query = authors_query.filter(Author.name.ilike(f'%{search_query}%'))
        
        authors = authors_query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('admin/authors.html', authors=authors, search_query=search_query)

    @app.route('/admin/authors/add', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def admin_add_author():
        if request.method == 'POST':
            name = request.form.get('name')
            if name:
                new_author = Author(name=name)
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
        db.session.delete(author)
        db.session.commit()
        flash('Author deleted successfully.')
        return redirect(url_for('admin_authors'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
