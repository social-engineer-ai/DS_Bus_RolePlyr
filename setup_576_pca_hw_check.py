"""Create the BADM 576 PCA HW Check quiz on the live server.

7 MCQs, 10 points total, 7-minute timer, 2 attempts, answers shown after
submit. Pure auto-grade — no LLM grader. Just an integrity check that the
student actually engaged with the PCA Homework rather than copy-pasted.
"""

import json
import urllib.request
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


QUESTIONS = [
    {
        "order_index": 0,
        "points": 1,
        "question_text": (
            "The candidate table in Part A has three numeric features (years of experience, "
            "education, salary expectation). Each candidate is a point in:"
        ),
        "options": [
            "1D space",
            "3D space",
            "5D space (the number of candidates)",
            "75D space",
        ],
        "correct_answer": "3D space",
    },
    {
        "order_index": 1,
        "points": 1,
        "question_text": (
            "Salary expectation ($K) dominates the Euclidean distance because it uses much "
            "larger units than the other features. The standard fix is to:"
        ),
        "options": [
            "Drop salary expectation from the analysis",
            "Standardize all features (e.g., mean 0, SD 1) before computing distance",
            "Use only categorical features instead",
            "Take the square root of every value",
        ],
        "correct_answer": "Standardize all features (e.g., mean 0, SD 1) before computing distance",
    },
    {
        "order_index": 2,
        "points": 1,
        "question_text": (
            "For purely categorical attributes, the simple matching-based (Hamming) distance is:"
        ),
        "options": [
            "The squared difference between attribute codes",
            "The number of attributes on which two observations differ, divided by the total",
            "The number of attributes on which they match",
            "The Euclidean distance after one-hot encoding",
        ],
        "correct_answer": "The number of attributes on which two observations differ, divided by the total",
    },
    {
        "order_index": 3,
        "points": 2,
        "question_text": (
            "On the 388-cars dataset, PC1 had large negative loadings on retail price, dealer "
            "price, engine size, cylinders, horsepower, weight, wheelbase, length, and width — "
            "and large positive loadings on city MPG and highway MPG. The most natural "
            "plain-English name for PC1 is:"
        ),
        "options": [
            "Luxury vs. economy (price only)",
            "Overall car size and power vs. fuel efficiency",
            "Sportiness",
            "Domestic vs. imported",
        ],
        "correct_answer": "Overall car size and power vs. fuel efficiency",
    },
    {
        "order_index": 4,
        "points": 2,
        "question_text": (
            "On the same dataset, PC2 had near-zero loadings on engine size, cylinders, city "
            "MPG, and highway MPG. It had strong positive loadings on wheelbase, length, and "
            "width, and strong negative loadings on retail price, dealer price, and horsepower. "
            "PC2 most plausibly separates:"
        ),
        "options": [
            "Big, roomy, lower-priced vehicles (e.g., wagons / SUVs / minivans) from expensive, compact, sporty cars",
            "Cars by engine power alone",
            "Manual vs. automatic transmission",
            "Old model years vs. new model years",
        ],
        "correct_answer": "Big, roomy, lower-priced vehicles (e.g., wagons / SUVs / minivans) from expensive, compact, sporty cars",
    },
    {
        "order_index": 5,
        "points": 1,
        "question_text": (
            "PCA was given only a 10 × 75 word-presence matrix for the movie reviews — no "
            "genre labels — yet its 2D projection clustered reviews by genre. The best "
            "explanation is:"
        ),
        "options": [
            "PCA secretly used the labels via supervised learning",
            "The 75 vocabulary words were hand-picked to encode genre",
            "Reviews of the same genre share overlapping vocabulary; PCA finds directions of greatest variance, which here align with those genre-driven word-co-occurrence patterns",
            "PCA always recovers ground-truth clusters",
        ],
        "correct_answer": "Reviews of the same genre share overlapping vocabulary; PCA finds directions of greatest variance, which here align with those genre-driven word-co-occurrence patterns",
    },
    {
        "order_index": 6,
        "points": 2,
        "question_text": (
            "You run PCA on a 2D dataset whose points lie along a clear curved arc. PC1 and "
            "PC2 capture roughly equal variance, and projecting onto either one destroys the "
            "visible structure. The best diagnosis is:"
        ),
        "options": [
            "The features need to be standardized first",
            "PCA always needs at least three dimensions to work",
            "The structure is fundamentally non-linear; principal components are straight lines and cannot capture a curve",
            "The dataset is too small",
        ],
        "correct_answer": "The structure is fundamentally non-linear; principal components are straight lines and cannot capture a curve",
    },
]


def main():
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]
    print(f"Logged in as: {resp['user']['name']}")

    due = (datetime.utcnow() + timedelta(days=7)).isoformat()

    quiz_payload = {
        "course_id": COURSE_ID,
        "title": "BADM 576 PCA HW Check",
        "description": (
            "Quick multiple-choice check on the PCA Homework (distance, principal "
            "components, and when PCA helps). 7 questions, 10 points total, 7-minute "
            "timer, 2 attempts (best score counts). This is a short integrity check — "
            "if you actually worked through the homework, the questions should be "
            "straightforward."
        ),
        "max_attempts": 2,
        "time_limit_minutes": 7,
        "due_date": due,
        "is_active": True,
        "show_answers_after_submit": True,
        "require_all_questions": True,
        "use_llm_grader": False,
        "questions": [
            {
                "question_type": "mcq",
                "question_text": q["question_text"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "points": q["points"],
                "order_index": q["order_index"],
            }
            for q in QUESTIONS
        ],
    }

    quiz = api_call("POST", "/api/v1/quizzes", quiz_payload, token)

    print()
    print("=" * 60)
    print("QUIZ CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Quiz ID: {quiz['id']}")
    print(f"Title: {quiz['title']}")
    print(f"Questions: {quiz['question_count']}")
    print(f"Total Points: {quiz['total_points']}")
    print(f"Due: {due}")
    print()
    print(f"Students: http://3.90.88.174:3002/quizzes")
    print(f"Instructor: http://3.90.88.174:3002/instructor/quizzes")


if __name__ == "__main__":
    main()
