"""update v0.72_3

Revision ID: 6cc2f1ca7e50
Revises: 6d88e8e532e3
Create Date: 2018-03-26 13:57:35.948776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6cc2f1ca7e50'
down_revision = '6d88e8e532e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('musers', 'about_me')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('musers', sa.Column('about_me', mysql.TEXT(), nullable=True))
    # ### end Alembic commands ###
