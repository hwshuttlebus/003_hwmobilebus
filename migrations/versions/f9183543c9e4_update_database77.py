"""update database77

Revision ID: f9183543c9e4
Revises: f0dd92537763
Create Date: 2018-01-26 14:34:01.850352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9183543c9e4'
down_revision = 'f0dd92537763'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mstations', sa.Column('bus_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'mstations', 'mbuses', ['bus_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mstations', type_='foreignkey')
    op.drop_column('mstations', 'bus_id')
    # ### end Alembic commands ###
