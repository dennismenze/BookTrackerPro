from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Book, Author, List, UserBook
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

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
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/api/authors/<int:id>')
@login_required
def api_author_detail(id):
    author = Author.query.options(joinedload(Author.books)).get_or_404(id)
    books = []
    for book in author.books:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book.id).first()
        books.append({
            'id': book.id,
            'title': book.title,
            'cover_image_url': book.cover_image_url,
            'is_read': user_book.is_read if user_book else False
        })
    return jsonify({
        'id': author.id,
        'name': author.name,
        'image_url': author.image_url,
        'books': books
    })

@app.route('/api/books/<int:id>/toggle-read', methods=['POST'])
@login_required
def toggle_read_status(id):
    user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=id).first()
    if user_book:
        user_book.is_read = not user_book.is_read
    else:
        user_book = UserBook(user_id=current_user.id, book_id=id, is_read=True)
        db.session.add(user_book)
    db.session.commit()
    return jsonify({'success': True, 'is_read': user_book.is_read})

@app.route('/author/<int:id>')
@login_required
def author_detail(id):
    return render_template('author/detail.html', author_id=id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
