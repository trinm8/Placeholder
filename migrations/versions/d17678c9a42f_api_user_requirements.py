"""api user requirements

Revision ID: d17678c9a42f
Revises: 4ceebfeb21c7
Create Date: 2020-03-05 15:17:36.062966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd17678c9a42f'
down_revision = '4ceebfeb21c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('firstname', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_user_firstname'), 'user', ['firstname'], unique=False)
    op.drop_index('ix_user_email', table_name='user')
    op.drop_index('ix_user_name', table_name='user')
    op.drop_column('user', 'email')
    op.drop_column('user', 'name')
    op.drop_column('user', 'age')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('name', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('email', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.create_index('ix_user_name', 'user', ['name'], unique=False)
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.drop_index(op.f('ix_user_firstname'), table_name='user')
    op.drop_column('user', 'firstname')
    # ### end Alembic commands ###
