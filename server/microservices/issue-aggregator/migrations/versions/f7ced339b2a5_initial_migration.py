"""Initial migration

Revision ID: f7ced339b2a5
Revises: 472e4582de9f
Create Date: 2025-02-25 18:04:30.153537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7ced339b2a5'
down_revision: Union[str, None] = '472e4582de9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'created_at',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.DateTime(),
               postgresql_using="created_at::timestamp without time zone",
               existing_nullable=True)
    op.alter_column('issues', 'updated_at',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.DateTime(),
               postgresql_using="updated_at::timestamp without time zone",
               existing_nullable=True)
    op.add_column('repositories', sa.Column('language', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('repositories', 'language')
    op.alter_column('issues', 'updated_at',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=50),
               postgresql_using="created_at::text",
               existing_nullable=True)
    op.alter_column('issues', 'created_at',
               existing_type=sa.DateTime(),
               postgresql_using="updated_at::text",
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
    # ### end Alembic commands ###
