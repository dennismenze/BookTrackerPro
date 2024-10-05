
"""Convert string fields to JSON

Revision ID: convert_string_to_json
Revises: da2aa1cc6a9e
Create Date: 2024-10-05 07:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
import json

# revision identifiers, used by Alembic.
revision = 'convert_string_to_json'
down_revision = 'da2aa1cc6a9e'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Convert Book title and description
    books = connection.execute(sa.text("SELECT id, title, description FROM books")).fetchall()
    for book in books:
        new_title = json.dumps({"en": book.title}) if book.title else json.dumps({})
        new_description = json.dumps({"en": book.description}) if book.description else json.dumps({})
        connection.execute(
            sa.text("UPDATE books SET title = :title, description = :description WHERE id = :id"),
            {"id": book.id, "title": new_title, "description": new_description}
        )

    # Convert Author name and bio
    authors = connection.execute(sa.text("SELECT id, name, bio FROM authors")).fetchall()
    for author in authors:
        new_name = json.dumps({"en": author.name}) if author.name else json.dumps({})
        new_bio = json.dumps({"en": author.bio}) if author.bio else json.dumps({})
        connection.execute(
            sa.text("UPDATE authors SET name = :name, bio = :bio WHERE id = :id"),
            {"id": author.id, "name": new_name, "bio": new_bio}
        )

    # Convert List name and description
    lists = connection.execute(sa.text("SELECT id, name, description FROM lists")).fetchall()
    for list_ in lists:
        new_name = json.dumps({"en": list_.name}) if list_.name else json.dumps({})
        new_description = json.dumps({"en": list_.description}) if list_.description else json.dumps({})
        connection.execute(
            sa.text("UPDATE lists SET name = :name, description = :description WHERE id = :id"),
            {"id": list_.id, "name": new_name, "description": new_description}
        )

    # Convert Post body
    posts = connection.execute(sa.text("SELECT id, body FROM posts")).fetchall()
    for post in posts:
        new_body = json.dumps({"en": post.body}) if post.body else json.dumps({})
        connection.execute(
            sa.text("UPDATE posts SET body = :body WHERE id = :id"),
            {"id": post.id, "body": new_body}
        )

def downgrade():
    connection = op.get_bind()

    # Revert Book title and description
    books = connection.execute(sa.text("SELECT id, title, description FROM books")).fetchall()
    for book in books:
        old_title = json.loads(book.title).get("en", "") if book.title else ""
        old_description = json.loads(book.description).get("en", "") if book.description else ""
        connection.execute(
            sa.text("UPDATE books SET title = :title, description = :description WHERE id = :id"),
            {"id": book.id, "title": old_title, "description": old_description}
        )

    # Revert Author name and bio
    authors = connection.execute(sa.text("SELECT id, name, bio FROM authors")).fetchall()
    for author in authors:
        old_name = json.loads(author.name).get("en", "") if author.name else ""
        old_bio = json.loads(author.bio).get("en", "") if author.bio else ""
        connection.execute(
            sa.text("UPDATE authors SET name = :name, bio = :bio WHERE id = :id"),
            {"id": author.id, "name": old_name, "bio": old_bio}
        )

    # Revert List name and description
    lists = connection.execute(sa.text("SELECT id, name, description FROM lists")).fetchall()
    for list_ in lists:
        old_name = json.loads(list_.name).get("en", "") if list_.name else ""
        old_description = json.loads(list_.description).get("en", "") if list_.description else ""
        connection.execute(
            sa.text("UPDATE lists SET name = :name, description = :description WHERE id = :id"),
            {"id": list_.id, "name": old_name, "description": old_description}
        )

    # Revert Post body
    posts = connection.execute(sa.text("SELECT id, body FROM posts")).fetchall()
    for post in posts:
        old_body = json.loads(post.body).get("en", "") if post.body else ""
        connection.execute(
            sa.text("UPDATE posts SET body = :body WHERE id = :id"),
            {"id": post.id, "body": old_body}
        )
