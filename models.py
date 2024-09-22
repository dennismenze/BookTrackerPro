from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer,
                          db.ForeignKey('authors.id'),
                          nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    author = db.relationship('Author', back_populates='books')
    lists = db.relationship('List',
                            secondary='book_list',
                            back_populates='books')


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    books = db.relationship('Book', back_populates='author')


class List(db.Model):
    __tablename__ = 'lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    books = db.relationship('Book',
                            secondary='book_list',
                            back_populates='lists')


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
