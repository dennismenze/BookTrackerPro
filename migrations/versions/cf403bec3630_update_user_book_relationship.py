"""Update user-book relationship

Revision ID: cf403bec3630
Revises: 25cc5cfb32dc
Create Date: 2024-09-23 14:43:40.076442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf403bec3630'
down_revision = '25cc5cfb32dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_book',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'book_id')
    )
    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.drop_constraint('fk_book_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)

    with op.batch_alter_table('books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.create_foreign_key('fk_book_user_id', 'users', ['user_id'], ['id'])

    op.drop_table('user_book')
    # ### end Alembic commands ###
