"""change mbus table

Revision ID: 18a007c44b17
Revises: 4e298ad5ce0b
Create Date: 2018-03-02 12:56:10.035753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18a007c44b17'
down_revision = '4e298ad5ce0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mbuses', sa.Column('number', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mbuses', 'number')
    # ### end Alembic commands ###