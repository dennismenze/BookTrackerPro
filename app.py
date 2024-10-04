from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Book, Author, List, UserBook, Post
from functools import wraps
from sqlalchemy import func
from flask_migrate import Migrate
from routes import book_routes, author_routes, list_routes, goal_routes
from io import BytesIO
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(book_routes.bp, url_prefix='/book')
app.register_blueprint(author_routes.bp, url_prefix='/author')
app.register_blueprint(list_routes.bp, url_prefix='/list')
app.register_blueprint(goal_routes.bp, url_prefix='/goal')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    if not current_user.is_authenticated:
        user = User.query.filter_by(username='test').first()
        if user:
            login_user(user)
    g.user = current_user

@app.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Fetch recent activities
    recent_activities = []
    
    # Recent books read
    recent_books = UserBook.query.filter_by(user_id=user.id).filter(UserBook.read_date.isnot(None)).order_by(UserBook.read_date.desc()).limit(5).all()
    for user_book in recent_books:
        recent_activities.append({
            'type': 'book_read',
            'book': user_book.book,
            'timestamp': datetime.combine(user_book.read_date, datetime.min.time())
        })
    
    # Recent lists created
    recent_lists = List.query.filter_by(user_id=user.id).order_by(List.id.desc()).limit(5).all()
    for list_item in recent_lists:
        recent_activities.append({
            'type': 'list_created',
            'list': list_item,
            'timestamp': datetime.fromtimestamp(list_item.id)  # Assuming id is a Unix timestamp
        })
    
    # Recent posts
    recent_posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).limit(5).all()
    for post in recent_posts:
        recent_activities.append({
            'type': 'post_created',
            'post': post,
            'timestamp': post.timestamp
        })
    
    # Sort all activities by timestamp (most recent first)
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Standardize timestamps
    for activity in recent_activities:
        activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('profile.html', user=user, recent_activities=recent_activities[:10])

@app.route('/profile_image/<int:user_id>')
def profile_image(user_id):
    user = User.query.get_or_404(user_id)
    if user.profile_image:
        return send_file(BytesIO(user.profile_image), mimetype='image/jpeg')
    else:
        return send_file('static/images/default-profile.png', mimetype='image/png')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Add logic for handling GET and POST requests
    return render_template('edit_profile.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
