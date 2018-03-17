"""addgps

Revision ID: 16d2747d2415
Revises: 18a007c44b17
Create Date: 2018-03-07 16:59:56.855252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16d2747d2415'
down_revision = '18a007c44b17'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mstations', sa.Column('gpsdstnew', sa.Float(precision='10,2'), nullable=True))
    op.add_column('mstations', sa.Column('gpsdstold', sa.Float(precision='10,2'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mstations', 'gpsdstold')
    op.drop_column('mstations', 'gpsdstnew')
    # ### end Alembic commands ###