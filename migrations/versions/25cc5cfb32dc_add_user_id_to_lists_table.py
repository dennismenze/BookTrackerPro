"""Add user_id to lists table

Revision ID: 25cc5cfb32dc
Revises: 
Create Date: 2023-09-23 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25cc5cfb32dc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to lists table
    with op.batch_alter_table('lists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_list_user_id', 'users', ['user_id'], ['id'])

    # Add user_id column to books table with a default value
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_book_user_id', 'users', ['user_id'], ['id'])

    # Update existing books with a default user_id (you may want to adjust this logic)
    op.execute("UPDATE books SET user_id = (SELECT id FROM users LIMIT 1) WHERE user_id IS NULL")

    # Now make the user_id column non-nullable
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.alter_column('user_id', nullable=False)


def downgrade():
    with op.batch_alter_table('lists', schema=None) as batch_op:
        batch_op.drop_constraint('fk_list_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_constraint('fk_book_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')
