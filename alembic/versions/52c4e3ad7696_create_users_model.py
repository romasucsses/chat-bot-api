"""create users model

Revision ID: 52c4e3ad7696
Revises: 
Create Date: 2024-10-13 16:54:41.462790
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '52c4e3ad7696'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bot_plan_model',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('model_access', sa.Integer, nullable=False),
        sa.Column('description', sa.String, nullable=True),
    )
    op.create_table(
        'user_model',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String, unique=True, nullable=True),
        sa.Column('email', sa.String, unique=True, nullable=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('last_name', sa.String, nullable=True),
        sa.Column('date_joining', sa.Date, server_default=sa.func.current_date()),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, server_default=sa.true()),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('bot_plan_model.id'), nullable=True),
        sa.Column('at_store_id', sa.Integer, nullable=True),
    )
    op.create_table(
        'refresh_token',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('refresh_token', sa.String, index=True),
        sa.Column('user_id', sa.Integer, index=True),
        sa.Column('user_permission', sa.String, server_default='client'),
        sa.Column('user_store_id', sa.Integer, nullable=True),
        sa.Column('expires_in', sa.Integer, nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('refresh_token')
    op.drop_table('user_model')
    op.drop_table('bot_plan_model')

