"""Lenient regrade pass for the BADM 576 final quiz.

1. Push much-more-lenient grading instructions to the quiz.
2. Trigger LLM regrade on all submitted attempts (regrade=True).
3. Compare new vs snapshot; if any answer's new score is LOWER than the old,
   restore the old (leniency is upside-only; we never lower a student).
4. Recompute attempt totals.
5. Print updated scores.

Reads `snapshot_pre_lenient_regrade.csv` written by the prior dump.
"""

import csv
import json
import time
import urllib.request
from collections import defaultdict

API = "http://3.90.88.174:8000"
QUIZ_ID = "c400cb0d-9fc9-490e-83ab-6f93d7f0fac4"
SNAPSHOT_CSV = "snapshot_pre_lenient_regrade.csv"


LENIENT_INSTRUCTIONS = (
    "GRADING STANCE: Be GENEROUS. The instructor's explicit standard for this final quiz is: "
    "if the student's answer contains any clear hint of the right concept, reward it. Default "
    "toward the higher rubric tier on borderline answers. The goal is to credit understanding, "
    "not to penalize.\n\n"
    "IGNORE COMPLETELY:\n"
    "- English grammar, spelling, sentence structure, or fluency\n"
    "- Whether the student named a technical term (e.g., 'curse of dimensionality', 'Simpson's "
    "paradox', 'omitted variable bias', 'closed-loop'). The names are nice-to-have only.\n"
    "- Whether the answer is short, rough, or in broken English\n"
    "- Whether the student structured the answer formally\n\n"
    "REWARD:\n"
    "- Plain-language descriptions of the right idea, even if rough or partial\n"
    "- Concrete examples that show the student grasps the concept, even if the explanation is "
    "thin\n"
    "- Any answer that demonstrates the student knows WHY something happens, even if they can't "
    "articulate it cleanly\n"
    "- Partial understanding — if 60% of the idea is there, give full credit. If only 30% is "
    "there, still award meaningful partial credit (don't drop to 0 or 1 unless the answer is "
    "actually wrong or empty).\n\n"
    "RUBRIC APPLICATION:\n"
    "- The 'full' tier should be the DEFAULT for any answer where the right concept is clearly "
    "present, regardless of phrasing.\n"
    "- The 'partial' or 'partial-low' tier is for answers that are missing a piece OR clearly "
    "misunderstand part of the question — not for answers that are merely awkwardly worded.\n"
    "- 'minimal' (1 point) is for answers that gesture at something tangentially related.\n"
    "- 'none' (0) is reserved for blank answers, fundamentally wrong answers, or answers that "
    "address a completely different question.\n\n"
    "PLAIN-LANGUAGE EQUIVALENTS to credit fully:\n"
    "- 'omitted variable' / 'confounding' → 'something else mixed in', 'absorbing another "
    "variable', 'picking up the effect of...', 'because we ignored X'\n"
    "- 'selection bias' → 'only training on the people we approved', 'rejected people are not "
    "in the data'\n"
    "- 'curse of dimensionality' → 'too many features makes everything look unique', 'distances "
    "become similar', 'cannot tell who is similar'\n"
    "- 'closed-loop / popularity loop' → 'recommended songs get more listens, so they get "
    "recommended more', 'rich get richer', 'feedback loop'\n"
    "- 'Simpson's paradox' → 'the picture changes when you split by group', 'aggregate "
    "misleads', 'subgroup tells different story'\n"
    "- 'precision / recall' → 'of the ones we caught', 'of the ones we predicted'\n\n"
    "FINAL CHECK BEFORE SCORING: ask yourself, 'Does this student understand the idea, even "
    "roughly?' If yes, score full or near-full. Many students are ESL — rough English does NOT "
    "mean weak comprehension. When in doubt, round UP."
)


def api_call(method, endpoint, data=None, token=None, timeout=600):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{API}{endpoint}", data=body, headers=headers, method=method)
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read())


def main():
    # 1. Login
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]
    print(f"Logged in as: {resp['user']['name']}")

    # 2. Load the snapshot
    snapshot = {}
    with open(SNAPSHOT_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            snapshot[row["answer_id"]] = {
                "old_points": float(row["old_points"]),
                "max_points": float(row["max_points"]),
                "old_reasoning": row["old_reasoning"],
                "attempt_id": row["attempt_id"],
                "q_num": int(row["q_num"]),
            }
    print(f"Loaded snapshot: {len(snapshot)} answers")

    # 3. Push lenient grading_instructions to the quiz
    print("\nUpdating grading_instructions on the quiz...")
    api_call(
        "PUT",
        f"/api/v1/quizzes/{QUIZ_ID}",
        {"grading_instructions": LENIENT_INSTRUCTIONS},
        token,
    )
    print("Instructions updated.")

    # 4. Trigger regrade=True on all submitted attempts
    print("\nTriggering regrade=true on all submitted attempts...")
    print("(420 LLM calls at up to 5 concurrent — will take a few minutes.)")
    t0 = time.time()
    result = api_call(
        "POST",
        f"/api/v1/quizzes/{QUIZ_ID}/grade-all-with-llm?regrade=true",
        token=token,
        timeout=900,
    )
    elapsed = time.time() - t0
    print(f"Regrade complete in {elapsed:.1f}s: {result}")

    # The next step (compare + restore old where new < old) must read from DB
    # post-regrade. We do that in a separate post-step via psql + a small
    # restoration UPDATE. For now, exit. The companion script
    # `lenient_regrade_postcheck.py` handles step 5+.
    print("\nNext: run lenient_regrade_postcheck.py to apply max(old,new) and recompute totals.")


if __name__ == "__main__":
    main()
