"""Initial schema — all tables including pilot features.

Revision ID: 001_initial
Revises:
Create Date: 2026-03-04
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("student", "instructor", "admin", name="userrole"),
            nullable=False,
            server_default="student",
        ),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- courses ---
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "instructor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- enrollments ---
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("student", "ta", "instructor", name="enrollmentrole"),
            nullable=False,
            server_default="student",
        ),
        sa.UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

    # --- rubrics ---
    op.create_table(
        "rubrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("criteria", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- personas ---
    op.create_table(
        "personas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("background", sa.Text(), nullable=True),
        sa.Column("personality", sa.Text(), nullable=True),
        sa.Column("concerns", postgresql.JSONB(), nullable=True),
        sa.Column("required_questions", postgresql.JSONB(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- scenarios ---
    op.create_table(
        "scenarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "persona_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("personas.id"),
            nullable=False,
        ),
        sa.Column(
            "rubric_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rubrics.id"),
            nullable=False,
        ),
        sa.Column("is_practice", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("max_turns", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- assignments ---
    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=False,
        ),
        sa.Column(
            "scenario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scenarios.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- conversations ---
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "scenario_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scenarios.id"),
            nullable=False,
        ),
        sa.Column(
            "assignment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assignments.id"),
            nullable=True,
        ),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column(
            "mode",
            sa.Enum("practice", "graded", name="conversationmode"),
            nullable=False,
            server_default="practice",
        ),
        sa.Column(
            "status",
            sa.Enum("in_progress", "completed", "abandoned", name="conversationstatus"),
            nullable=False,
            server_default="in_progress",
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        # Pilot features
        sa.Column("violation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("violation_log", postgresql.JSONB(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("total_active_seconds", sa.Integer(), nullable=True),
    )

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("student", "stakeholder", name="messagerole"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # --- grades ---
    op.create_table(
        "grades",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "rubric_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("rubrics.id"),
            nullable=False,
        ),
        sa.Column("criteria_scores", postgresql.JSONB(), nullable=False),
        sa.Column("total_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("overall_feedback", sa.Text(), nullable=True),
        sa.Column("strengths", postgresql.JSONB(), nullable=True),
        sa.Column("areas_for_improvement", postgresql.JSONB(), nullable=True),
        sa.Column("ai_confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column(
            "graded_by",
            sa.Enum("ai", "instructor", name="gradedby"),
            nullable=False,
            server_default="ai",
        ),
        sa.Column("instructor_override", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("graded_at", sa.DateTime(), nullable=False),
    )

    # --- daily_analytics ---
    op.create_table(
        "daily_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("courses.id"),
            nullable=False,
        ),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_conversations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_practice", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_graded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("common_struggles", postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint("course_id", "date", name="uq_course_date"),
    )


def downgrade() -> None:
    op.drop_table("daily_analytics")
    op.drop_table("grades")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("assignments")
    op.drop_table("scenarios")
    op.drop_table("personas")
    op.drop_table("rubrics")
    op.drop_table("enrollments")
    op.drop_table("courses")
    op.drop_table("users")

    # Drop enum types
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="enrollmentrole").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="conversationmode").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="conversationstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="messagerole").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="gradedby").drop(op.get_bind(), checkfirst=True)
