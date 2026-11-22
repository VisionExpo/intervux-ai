"""Reconcile the migrated schema with the ORM models.

Migrations 001-004 never created the recruiter interview tables and created
``job_posts`` with only a subset of the columns the ORM maps, so every recruiter
job-post / report endpoint failed on a database built through Alembic. This
revision closes that gap:

* job_posts: add recruiter_id, required_skills, salary_range_min/max,
  employment_type, location, interview_focus_areas, evaluation_weights.
  recruiter_id is backfilled from the legacy ``created_by`` column, which is
  kept (no data is dropped).
* create interviews, interview_questions, interview_replay_segments.
* indexes for the ownership and lookup paths:
  job_posts.recruiter_id, candidates.job_post_id, interviews.candidate_id,
  interview_questions.interview_id, interview_replay_segments.interview_id,
  mock_interviews.session_id (hot path of the WebSocket ownership fence).

Every step checks the live schema first. Some databases were created with
``Base.metadata.create_all`` and then stamped (AUTO_STAMP_DB), so the objects
may already exist; upgrading such a database must be a no-op for them.

Not changed here (follow-ups): a foreign key on candidates.job_post_id (legacy
rows may hold dangling IDs) and the unused ``job_skills`` table.

Revision ID: 005
Revises: 004
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


JOB_POST_COLUMNS = (
    sa.Column("recruiter_id", sa.String(), nullable=True),
    sa.Column("required_skills", sa.JSON(), nullable=True),
    sa.Column("salary_range_min", sa.Integer(), nullable=True),
    sa.Column("salary_range_max", sa.Integer(), nullable=True),
    sa.Column("employment_type", sa.String(), nullable=True, server_default="full-time"),
    sa.Column("location", sa.String(), nullable=True),
    sa.Column("interview_focus_areas", sa.JSON(), nullable=True),
    sa.Column("evaluation_weights", sa.JSON(), nullable=True),
)

# (index name, table, columns)
INDEXES = (
    ("ix_job_posts_recruiter_id", "job_posts", ["recruiter_id"]),
    ("ix_candidates_job_post_id", "candidates", ["job_post_id"]),
    ("ix_interviews_candidate_id", "interviews", ["candidate_id"]),
    ("ix_interview_questions_interview_id", "interview_questions", ["interview_id"]),
    ("ix_interview_replay_segments_interview_id", "interview_replay_segments", ["interview_id"]),
    ("ix_mock_interviews_session_id", "mock_interviews", ["session_id"]),
)


def _inspector():
    return sa.inspect(op.get_bind())


def _columns(table: str) -> set[str]:
    return {column["name"] for column in _inspector().get_columns(table)}


def _indexes(table: str) -> set[str]:
    return {index["name"] for index in _inspector().get_indexes(table)}


def upgrade() -> None:
    tables = set(_inspector().get_table_names())

    # --- job_posts columns -------------------------------------------------
    existing = _columns("job_posts")
    for column in JOB_POST_COLUMNS:
        if column.name not in existing:
            op.add_column("job_posts", column.copy())

    if "created_by" in _columns("job_posts"):
        op.execute(
            "UPDATE job_posts SET recruiter_id = created_by "
            "WHERE recruiter_id IS NULL AND created_by IS NOT NULL"
        )

    # --- recruiter interview tables -----------------------------------------
    if "interviews" not in tables:
        op.create_table(
            "interviews",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("candidate_id", sa.String(), nullable=False),
            sa.Column("role", sa.String(), nullable=False),
            sa.Column("overall_score", sa.Float(), nullable=True),
            sa.Column("technical_score", sa.Float(), nullable=True),
            sa.Column("communication_score", sa.Float(), nullable=True),
            sa.Column("problem_solving_score", sa.Float(), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "interview_questions" not in tables:
        op.create_table(
            "interview_questions",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("interview_id", sa.String(), nullable=False),
            sa.Column("question", sa.Text(), nullable=False),
            sa.Column("answer", sa.Text(), nullable=True),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("feedback", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "interview_replay_segments" not in tables:
        op.create_table(
            "interview_replay_segments",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("interview_id", sa.String(), nullable=False),
            sa.Column("question", sa.Text(), nullable=False),
            sa.Column("transcript", sa.Text(), nullable=True),
            sa.Column("audio_url", sa.String(), nullable=True),
            sa.Column("score", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    # --- indexes ------------------------------------------------------------
    for name, table, columns in INDEXES:
        if name not in _indexes(table):
            op.create_index(name, table, columns)


def downgrade() -> None:
    tables = set(_inspector().get_table_names())

    for name, table, _columns_ in reversed(INDEXES):
        if table in tables and name in _indexes(table):
            op.drop_index(name, table_name=table)

    for table in ("interview_replay_segments", "interview_questions", "interviews"):
        if table in tables:
            op.drop_table(table)

    # created_by is kept by upgrade, so dropping recruiter_id loses no ownership data
    # that existed before 005.
    existing = _columns("job_posts")
    for column in reversed(JOB_POST_COLUMNS):
        if column.name in existing:
            op.drop_column("job_posts", column.name)
