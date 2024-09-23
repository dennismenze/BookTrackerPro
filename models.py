from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

user_book = db.Table(
    'user_book',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True)
)

class UserBook(db.Model):
    __tablename__ = 'user_books'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
    is_read = db.Column(db.Boolean, default=False)
    user = db.relationship("User", back_populates="user_books")
    book = db.relationship("Book", back_populates="user_books")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    books = db.relationship('Book', secondary=user_book, back_populates='users')
    user_books = db.relationship("UserBook", back_populates="user")
    lists = db.relationship('List', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password,
                                                    method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer,
                          db.ForeignKey('authors.id'),
                          nullable=False)
    users = db.relationship('User', secondary=user_book, back_populates='books')
    user_books = db.relationship("UserBook", back_populates="book")
    author = db.relationship('Author', back_populates='books')
    lists = db.relationship('List',
                            secondary='book_list',
                            back_populates='books')
    
    # Fields for Google Books API integration
    isbn = db.Column(db.String(20))
    description = db.Column(db.Text)
    cover_image_url = db.Column(db.String(255))
    page_count = db.Column(db.Integer)
    published_date = db.Column(db.String(20))


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    books = db.relationship('Book', back_populates='author')


class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    books = db.relationship('Book',
                            secondary='book_list',
                            back_populates='lists')

    @property
    def is_public(self):
        return self.user_id is None


book_list = db.Table(
    'book_list',
    db.Column('book_id',
              db.Integer,
              db.ForeignKey('books.id'),
              primary_key=True),
    db.Column('list_id',
              db.Integer,
              db.ForeignKey('lists.id'),
              primary_key=True))
