"""empty message

Revision ID: 854b5ab6e19d
Revises: 8ce715be7ef5
Create Date: 2022-06-29 19:14:15.268882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '854b5ab6e19d'
down_revision = '8ce715be7ef5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('order', 'status',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)
    op.add_column('product', sa.Column('category', sa.String(length=50), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'category')
    op.alter_column('order', 'status',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    # ### end Alembic commands ###
