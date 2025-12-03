"""Add trial_balance_entries table

Revision ID: 5d9f8c7b2a1a
Revises: e8e213a
Create Date: 2024-05-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d9f8c7b2a1a'
down_revision = 'e8e213a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('trial_balance_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('engagement_id', sa.Integer(), nullable=True),
    sa.Column('account_code', sa.String(), nullable=True),
    sa.Column('account_description', sa.String(), nullable=True),
    sa.Column('initial_balance', sa.Float(), nullable=True),
    sa.Column('debits', sa.Float(), nullable=True),
    sa.Column('credits', sa.Float(), nullable=True),
    sa.Column('final_balance', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['engagement_id'], ['engagements.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trial_balance_entries_account_code'), 'trial_balance_entries', ['account_code'], unique=False)
    op.create_index(op.f('ix_trial_balance_entries_id'), 'trial_balance_entries', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_trial_balance_entries_id'), table_name='trial_balance_entries')
    op.drop_index(op.f('ix_trial_balance_entries_account_code'), table_name='trial_balance_entries')
    op.drop_table('trial_balance_entries')
