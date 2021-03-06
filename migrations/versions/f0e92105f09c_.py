"""empty message

Revision ID: f0e92105f09c
Revises: cf607325ffd2
Create Date: 2022-06-23 12:17:00.398782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0e92105f09c'
down_revision = 'cf607325ffd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'confirm_password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('confirm_password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
