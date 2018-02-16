"""update database4

Revision ID: 0cdbbcd3e00e
Revises: 21880da6c6df
Create Date: 2018-01-26 11:18:26.089268

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0cdbbcd3e00e'
down_revision = '21880da6c6df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mbuses', 'recordtime')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mbuses', sa.Column('recordtime', mysql.TIME(), nullable=True))
    # ### end Alembic commands ###
