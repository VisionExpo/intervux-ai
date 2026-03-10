"""Add candidate_portal tables (candidate_profiles, mock_interviews, notifications)

Revision ID: 003
Revises: 002
Create Date: 2024-01-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create candidate_profiles table
    op.create_table(
        'candidate_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('skills', sa.Text(), nullable=True),  # JSON string of skills list
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('education', sa.Text(), nullable=True),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('resume_score', sa.Float(), nullable=True),
        sa.Column('interview_score', sa.Float(), nullable=True),
        sa.Column('profile_score', sa.Float(), nullable=True),
        sa.Column('github_url', sa.String(), nullable=True),
        sa.Column('linkedin_url', sa.String(), nullable=True),
        sa.Column('mock_interviews_remaining', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    
    # Create mock_interviews table
    op.create_table(
        'mock_interviews',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('technical_score', sa.Float(), nullable=True),
        sa.Column('communication_score', sa.Float(), nullable=True),
        sa.Column('reasoning_score', sa.Float(), nullable=True),
        sa.Column('evaluation', sa.Text(), nullable=True),  # JSON string of evaluation
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='in_progress'),
        sa.Column('interview_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidate_profiles.id']),
    )
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    
    # Add index for faster queries
    op.create_index('idx_candidate_profiles_user_id', 'candidate_profiles', ['user_id'])
    op.create_index('idx_mock_interviews_candidate_id', 'mock_interviews', ['candidate_id'])
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_notifications_user_id', table_name='notifications')
    op.drop_index('idx_mock_interviews_candidate_id', table_name='mock_interviews')
    op.drop_index('idx_candidate_profiles_user_id', table_name='candidate_profiles')
    
    # Drop tables
    op.drop_table('notifications')
    op.drop_table('mock_interviews')
    op.drop_table('candidate_profiles')

