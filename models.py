from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json

db = SQLAlchemy()

user_book = db.Table('user_book',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class UserBook(db.Model):
    __tablename__ = 'user_books'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    read_date = db.Column(db.Date, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.Text, nullable=True)
    user = db.relationship("User", back_populates="user_books")
    book = db.relationship("Book", back_populates="user_books")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    books = db.relationship('Book', secondary=user_book, back_populates='users')
    user_books = db.relationship("UserBook", back_populates="user")
    lists = db.relationship('List', backref='user', lazy='dynamic')
    reading_goal = db.relationship('ReadingGoal', back_populates='user', uselist=False)
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    profile_image = db.Column(db.LargeBinary)
    date_joined = db.Column(db.DateTime, default=db.func.now())
    preferred_language = db.Column(db.String(5))

    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    users = db.relationship('User', secondary=user_book, back_populates='books')
    user_books = db.relationship("UserBook", back_populates="book")
    author = db.relationship('Author', back_populates='books')
    lists = db.relationship('List', secondary='book_list', back_populates='books')

    isbn = db.Column(db.String(20))
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(255))
    page_count = db.Column(db.Integer)
    published_date = db.Column(db.String(20))

    is_main_work = db.Column(db.Boolean, default=False)

    @property
    def average_rating(self):
        ratings = [ub.rating for ub in self.user_books if ub.rating is not None]
        return sum(ratings) / len(ratings) if ratings else None

    def __str__(self):
        return f"{self.get_title()} by {self.author.get_name()}"

    def get_title(self, lang='en'):
        if isinstance(self.title, str):
            try:
                title_dict = json.loads(self.title)
            except json.JSONDecodeError:
                return self.title
        else:
            title_dict = self.title
        
        if isinstance(title_dict, dict):
            return title_dict.get(lang, title_dict.get('en', ''))
        else:
            return str(title_dict)

    def get_description(self, lang='en'):
        if self.description:
            try:
                desc_dict = json.loads(self.description)
                return desc_dict.get(lang, desc_dict.get('en', ''))
            except json.JSONDecodeError:
                return self.description
        return ''

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    books = db.relationship('Book', back_populates='author')
    image_url = db.Column(db.String(255))
    bio = db.Column(db.Text)

    def __str__(self):
        return self.get_name()

    def get_name(self, lang='en'):
        if isinstance(self.name, str):
            try:
                name_dict = json.loads(self.name)
            except json.JSONDecodeError:
                return self.name
        else:
            name_dict = self.name
        
        if isinstance(name_dict, dict):
            return name_dict.get(lang, name_dict.get('en', ''))
        else:
            return str(name_dict)

    def get_bio(self, lang='en'):
        if self.bio:
            try:
                bio_dict = json.loads(self.bio)
                return bio_dict.get(lang, bio_dict.get('en', ''))
            except json.JSONDecodeError:
                return self.bio
        return ''

class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    books = db.relationship('Book', secondary='book_list', back_populates='lists')
    is_public = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

    def __str__(self):
        return f"{self.get_name()} (User: {self.user.username})"

    def get_name(self, lang='en'):
        try:
            name_dict = json.loads(self.name)
            return name_dict.get(lang, name_dict.get('en', ''))
        except json.JSONDecodeError:
            return self.name

    def get_description(self, lang='en'):
        if self.description:
            try:
                desc_dict = json.loads(self.description)
                return desc_dict.get(lang, desc_dict.get('en', ''))
            except json.JSONDecodeError:
                return self.description
        return ''

class BookList(db.Model):
    __tablename__ = 'book_list'
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), primary_key=True)
    rank = db.Column(db.Integer, default=0)
    
    book = db.relationship("Book", backref="book", viewonly=True)
    list = db.relationship("List", backref="list", viewonly=True)

    def __str__(self):
        return f"BookList: {self.book.get_title()} - {self.list.get_name()}"

class ReadingGoal(db.Model):
    __tablename__ = 'reading_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    goal_type = db.Column(db.String(20), nullable=False)  # 'books' or 'pages'
    target = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    user = db.relationship('User', back_populates='reading_goal')

    def __str__(self):
        return f"ReadingGoal: {self.user.username} - {self.goal_type} ({self.target})"

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __str__(self):
        return f"Post: {self.author.username} - {self.timestamp}"

    def get_body(self, lang='en'):
        if self.body:
            try:
                body_dict = json.loads(self.body)
                return body_dict.get(lang, body_dict.get('en', ''))
            except json.JSONDecodeError:
                return self.body
        return ''