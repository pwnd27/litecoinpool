"""empty message

Revision ID: bd3d1c6d3eb1
Revises: 21b3349856c8
Create Date: 2023-03-03 12:44:27.988373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd3d1c6d3eb1'
down_revision = '21b3349856c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('workers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workers_id'), 'workers', ['id'], unique=False)
    op.create_table('worker_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('worker_id', sa.Integer(), nullable=False),
    sa.Column('hash_rate', sa.Integer(), nullable=False),
    sa.Column('connected', sa.Boolean(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['worker_id'], ['workers.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_worker_info_id'), 'worker_info', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_worker_info_id'), table_name='worker_info')
    op.drop_table('worker_info')
    op.drop_index(op.f('ix_workers_id'), table_name='workers')
    op.drop_table('workers')
    # ### end Alembic commands ###
