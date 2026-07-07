"""Create the BADM 576 Week 7 ML Self-Authored Q&A Quiz on the live server."""

import urllib.request
import json
from datetime import datetime, timedelta

API = "http://3.90.88.174:8000"
COURSE_ID = "55555555-5555-5555-5555-555555555555"


def api_call(method, endpoint, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{API}{endpoint}", data=body, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


# Login
resp = api_call("POST", "/api/v1/auth/login", {
    "email": "instructor@stakeholdersim.edu",
    "password": "instructor123",
})
token = resp["access_token"]
print(f"Logged in as: {resp['user']['name']}")

# Create the self-authored quiz
due = (datetime.utcnow() + timedelta(days=7)).isoformat()

quiz = api_call("POST", "/api/v1/quizzes", {
    "course_id": COURSE_ID,
    "title": "BADM 576 — ML Process: Write Your Own Q&A",
    "description": (
        "Demonstrate your understanding of the 7-step ML process by writing your own "
        "questions and answers. For each topic below, create a thoughtful question that "
        "tests understanding of that concept, then write a complete answer. "
        "Your questions should be specific enough that they couldn't be answered with "
        "a simple definition — aim for questions that require reasoning or application."
    ),
    "max_attempts": 5,
    "time_limit_minutes": 45,
    "due_date": due,
    "is_active": True,
    "show_answers_after_submit": True,
    "questions": [
        {
            "question_type": "self_authored",
            "question_text": (
                "Task Definition (T): Write a question about how to define an ML task "
                "for a business problem. Your question should require the answerer to "
                "distinguish between regression and classification, or to precisely define "
                "what a model should predict and why."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 0,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Data / Experience (E): Write a question about selecting the right data "
                "for an ML model. Your question should address one or more of: outcome variable "
                "selection, predictor choice, data quality (completeness, accuracy, recency), "
                "or data leakage risks."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 1,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Model Building: Write a question about constructing a linear regression model. "
                "Your question could involve writing the equation, reasoning about coefficient "
                "signs (betas), or explaining what the model structure represents."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 2,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Loss Function (P): Write a question about choosing a loss function. "
                "Your question should involve reasoning about symmetric vs asymmetric loss, "
                "or connecting the choice of loss function to specific business consequences "
                "(e.g., what happens when you overestimate vs underestimate)."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 3,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Gradient Descent: Write a question about how gradient descent finds optimal "
                "model parameters. Your question should go beyond definitions — ask about the "
                "role of the learning rate, why exhaustive search is impractical, or what "
                "convergence means in practice."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 4,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Inference / Prediction: Write a question that requires computing a prediction "
                "from a trained regression model, or interpreting what specific coefficients "
                "mean in business terms."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 5,
        },
        {
            "question_type": "self_authored",
            "question_text": (
                "Drift Analysis: Write a question about model drift. Your question should "
                "require distinguishing between data drift and concept drift, or identifying "
                "realistic scenarios that would cause a deployed model to degrade over time."
            ),
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": 6,
        },
    ],
}, token)

print()
print("=" * 60)
print("QUIZ CREATED SUCCESSFULLY!")
print("=" * 60)
print(f"Quiz ID: {quiz['id']}")
print(f"Title: {quiz['title']}")
print(f"Questions: {quiz['question_count']}")
print(f"Total Points: {quiz['total_points']}")
print(f"Max Attempts: 5")
print(f"Due: {due}")
print()
print(f"Students go to: http://3.90.88.174:3002/quizzes")
print(f"Instructor view: http://3.90.88.174:3002/instructor/quizzes")
