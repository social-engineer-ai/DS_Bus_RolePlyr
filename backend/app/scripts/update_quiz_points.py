"""Update BADM 558 quiz: 3 pts per question, answer any 5 (15 pts total).

Run with: python -m app.scripts.update_quiz_points
"""

from uuid import UUID
from app.database import SessionLocal
from app.models.quiz import Quiz, QuizQuestion

QUIZ_ID = UUID("aaaa0001-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def update_quiz():
    db = SessionLocal()
    try:
        quiz = db.query(Quiz).filter(Quiz.id == QUIZ_ID).first()
        if not quiz:
            print("Quiz not found.")
            return

        quiz.description = (
            "15 questions covering Kinesis Data Streams + Firehose, Glue ETL, "
            "and S3 + Athena. Answer any 5 questions (3 pts each, 15 pts total). "
            "Focus on WHY we use each service and KEY DECISIONS when configuring them."
        )

        questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == QUIZ_ID).all()
        for q in questions:
            q.points = 3

        db.commit()
        print(f"Updated quiz description and {len(questions)} questions to 3 pts each.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_quiz()
