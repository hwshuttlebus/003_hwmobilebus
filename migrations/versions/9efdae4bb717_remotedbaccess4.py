"""remotedbaccess4

Revision ID: 9efdae4bb717
Revises: f2f2b39109af
Create Date: 2018-04-01 18:01:30.336801

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9efdae4bb717'
down_revision = 'f2f2b39109af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('CarID', sa.String(length=20), nullable=True),
    sa.Column('DateTimes', sa.DateTime(), nullable=True),
    sa.Column('CardNo', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('CardNo')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    # ### end Alembic commands ###