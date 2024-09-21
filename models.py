from app import db
from sqlalchemy import Integer, String, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

book_list = Table(
    "book_list",
    db.metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("list_id", Integer, ForeignKey("list.id"))
)

class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("author.id"), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    lists: Mapped[list["List"]] = relationship(secondary=book_list, back_populates="books")

class Author(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

class List(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    books: Mapped[list["Book"]] = relationship(secondary=book_list, back_populates="lists")
