"""addgps2

Revision ID: a198a8aaed18
Revises: 16d2747d2415
Create Date: 2018-03-08 09:24:39.269807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a198a8aaed18'
down_revision = '16d2747d2415'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mbuses', sa.Column('curridx', sa.Integer(), nullable=True))
    op.add_column('mbuses', sa.Column('lefttime', sa.Integer(), nullable=True))
    op.drop_column('mstations', 'gpsdstnew')
    op.drop_column('mstations', 'gpsdstold')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mstations', sa.Column('gpsdstold', mysql.FLOAT(precision=10, scale=2), nullable=True))
    op.add_column('mstations', sa.Column('gpsdstnew', mysql.FLOAT(precision=10, scale=2), nullable=True))
    op.drop_column('mbuses', 'lefttime')
    op.drop_column('mbuses', 'curridx')
    # ### end Alembic commands ###
