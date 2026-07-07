"""Add LLM grading fields to quizzes, quiz_questions, quiz_answers.

Revision ID: 003_llm_grading
Revises: 002_add_quizzes
Create Date: 2026-04-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_llm_grading"
down_revision = "002_add_quizzes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # quizzes: scoring model + LLM grader config
    op.add_column("quizzes", sa.Column("require_all_questions", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("quizzes", sa.Column("use_llm_grader", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("quizzes", sa.Column("llm_grader_model", sa.String(64), nullable=True))
    op.add_column("quizzes", sa.Column("grading_instructions", sa.Text(), nullable=True))
    op.add_column("quizzes", sa.Column("hw_reference", sa.Text(), nullable=True))

    # quiz_questions: rubric + model answer + common wrong answers
    op.add_column("quiz_questions", sa.Column("rubric", postgresql.JSONB(), nullable=True))
    op.add_column("quiz_questions", sa.Column("model_answer", sa.Text(), nullable=True))
    op.add_column("quiz_questions", sa.Column("common_wrong_answers", sa.Text(), nullable=True))

    # quiz_answers: grader provenance + reasoning
    op.add_column("quiz_answers", sa.Column("grader_reasoning", sa.Text(), nullable=True))
    op.add_column("quiz_answers", sa.Column("graded_by", sa.String(16), nullable=False, server_default="none"))


def downgrade() -> None:
    op.drop_column("quiz_answers", "graded_by")
    op.drop_column("quiz_answers", "grader_reasoning")
    op.drop_column("quiz_questions", "common_wrong_answers")
    op.drop_column("quiz_questions", "model_answer")
    op.drop_column("quiz_questions", "rubric")
    op.drop_column("quizzes", "hw_reference")
    op.drop_column("quizzes", "grading_instructions")
    op.drop_column("quizzes", "llm_grader_model")
    op.drop_column("quizzes", "use_llm_grader")
    op.drop_column("quizzes", "require_all_questions")
