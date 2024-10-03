"""Add reading goals

Revision ID: 18193fa55da6
Revises: cb198b64b0ad
Create Date: 2024-10-03 13:51:23.681892

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18193fa55da6'
down_revision = 'cb198b64b0ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reading_goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('goal_type', sa.String(length=20), nullable=False),
    sa.Column('target', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reading_goals')
    # ### end Alembic commands ###
