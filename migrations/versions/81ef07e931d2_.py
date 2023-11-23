"""empty message

Revision ID: 81ef07e931d2
Revises: 866e107e3529
Create Date: 2023-11-23 16:50:39.042241

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '81ef07e931d2'
down_revision = '866e107e3529'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pc', schema=None) as batch_op:
        batch_op.add_column(sa.Column('service_tag', sa.String(length=50), nullable=False))
        batch_op.drop_index('serial_number')
        batch_op.create_unique_constraint(None, ['service_tag'])
        batch_op.drop_column('serial_number')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('pc', schema=None) as batch_op:
        batch_op.add_column(sa.Column('serial_number', mysql.VARCHAR(length=50), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('serial_number', ['serial_number'], unique=False)
        batch_op.drop_column('service_tag')

    # ### end Alembic commands ###
