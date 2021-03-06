"""initial migration

Revision ID: 27eebbd32d76
Revises: 
Create Date: 2018-01-08 16:08:44.804362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27eebbd32d76'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('buses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ebus_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('cz_name', sa.String(length=64), nullable=True),
    sa.Column('cz_phone', sa.String(length=30), nullable=True),
    sa.Column('sj_name', sa.String(length=64), nullable=True),
    sa.Column('sj_phone', sa.String(length=64), nullable=True),
    sa.Column('seat_num', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_buses_ebus_id'), 'buses', ['ebus_id'], unique=True)
    op.create_table('stations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ebus_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('time', sa.Time(), nullable=True),
    sa.Column('dirtocompany', sa.Boolean(), nullable=True),
    sa.Column('lat', sa.Float(precision='11,8'), nullable=True),
    sa.Column('lon', sa.Float(precision='11,8'), nullable=True),
    sa.Column('bus_id_fromebus', sa.Integer(), nullable=True),
    sa.Column('bus_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bus_id'], ['buses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stations_ebus_id'), 'stations', ['ebus_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stations_ebus_id'), table_name='stations')
    op.drop_table('stations')
    op.drop_index(op.f('ix_buses_ebus_id'), table_name='buses')
    op.drop_table('buses')
    # ### end Alembic commands ###
