"""delseat_num

Revision ID: 367eca13f30b
Revises: 3ab434d1afe1
Create Date: 2018-03-28 12:28:27.127816

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '367eca13f30b'
down_revision = '3ab434d1afe1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mbuses', 'seat_num')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mbuses', sa.Column('seat_num', mysql.VARCHAR(length=64), nullable=True))
    # ### end Alembic commands ###