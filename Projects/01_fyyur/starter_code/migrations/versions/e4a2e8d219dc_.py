"""empty message

Revision ID: e4a2e8d219dc
Revises: 507d31715f02
Create Date: 2020-06-03 12:09:30.827212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4a2e8d219dc'
down_revision = '507d31715f02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist', sa.Integer(), nullable=False),
    sa.Column('venue', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['artist'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Show')
    # ### end Alembic commands ###