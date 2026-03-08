"""Add job_posts, job_skills tables and update candidates

Revision ID: 002
Revises: 001
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create job_posts table
    op.create_table(
        'job_posts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('experience_level', sa.String(), nullable=False, server_default='mid'),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('ai_interview_enabled', sa.String(), nullable=False, server_default='false'),
        sa.Column('interview_limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create job_skills table
    op.create_table(
        'job_skills',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_post_id', sa.String(), nullable=False),
        sa.Column('skill_name', sa.String(), nullable=False),
        sa.Column('is_required', sa.String(), nullable=False, server_default='true'),
        sa.Column('proficiency_level', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['job_post_id'], ['job_posts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add new columns to candidates table
    op.add_column('candidates', sa.Column('status', sa.String(), nullable=False, server_default='invited'))
    op.add_column('candidates', sa.Column('job_post_id', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('interview_link', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('interview_link_expires_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove new columns from candidates
    op.drop_column('candidates', 'interview_link_expires_at')
    op.drop_column('candidates', 'interview_link')
    op.drop_column('candidates', 'job_post_id')
    op.drop_column('candidates', 'status')
    
    # Drop job_skills table
    op.drop_table('job_skills')
    
    # Drop job_posts table
    op.drop_table('job_posts')

