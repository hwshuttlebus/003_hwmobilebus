"""update database2

Revision ID: f52da2515b24
Revises: dd50eea8d165
Create Date: 2018-01-25 16:36:54.252037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f52da2515b24'
down_revision = 'dd50eea8d165'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('registration_ibfk_2', 'registration', type_='foreignkey')
    op.create_foreign_key(None, 'registration', 'musers', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'registration', type_='foreignkey')
    op.create_foreign_key('registration_ibfk_2', 'registration', 'mbuses', ['user_id'], ['id'])
    # ### end Alembic commands ###
