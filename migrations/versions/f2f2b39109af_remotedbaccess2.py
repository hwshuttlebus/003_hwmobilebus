"""remotedbaccess2

Revision ID: f2f2b39109af
Revises: 17ee6a818239
Create Date: 2018-04-01 17:34:54.222865

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f2f2b39109af'
down_revision = '17ee6a818239'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('CarID', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('DateTimes', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
