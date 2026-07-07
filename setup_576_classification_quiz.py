"""Create the BADM 576 HW3 Classification Quiz on the live server.

Ships rubric + model answers + LLM grading config so the instructor can
trigger Opus 4.7 grading and review each LLM-assigned score.
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


def rubric(full: str, partial: str, minimal: str, none: str) -> list:
    return [
        {"label": "full", "points": 4, "criteria": full},
        {"label": "partial", "points": 3, "criteria": "Strong but missing a piece: " + partial},
        {"label": "partial-low", "points": 2, "criteria": "Partially on track: " + partial},
        {"label": "minimal", "points": 1, "criteria": minimal},
        {"label": "none", "points": 0, "criteria": none},
    ]


GRADING_INSTRUCTIONS = (
    "This quiz checks whether students grasped the big ideas from the Classification HW, not "
    "whether they memorized terminology. Reward understanding expressed in plain language — if "
    "a student describes the right concept in their own words, give full credit even without "
    "technical terms. When a student uses technical terms, look for evidence they understand "
    "what the terms mean and credit the understanding, not the vocabulary alone. Partial credit "
    "(0, 1, 2, 3, or 4 points) is allowed and expected. Plain-language equivalents to look for: "
    "'confounding' or 'omitted variable bias' → 'picking up something else', 'mixed together', "
    "'absorbing another variable's effect'; "
    "'false positive' / 'false negative' → 'wrong promotion', 'missed promotion'; "
    "'bias vs variance' → 'how wrong on average vs how much it wiggles'."
)

HW_REFERENCE = (
    "Students completed the Classification HW on the Beta Group promotion dataset. "
    "Parts referenced in the questions: Part B ran a logistic regression and observed that "
    "the coefficient on `gender` changed when `avg_training_score` was dropped. "
    "Part C explored cutoff tuning with FN cost $1,000 and FP cost $500, then a sensitivity "
    "case in C5 where FN cost dropped to $400. Part E tuned Decision Tree hyperparameters "
    "including `min_samples_split` and `max_depth`. "
    "This quiz multiplies the Classification HW grade, so grading should be careful and fair."
)


QUESTIONS = [
    {
        "order_index": 0,
        "points": 4,
        "question_text": (
            "Sophia gave us two problems: (a) figure out whether age or gender affects promotion "
            "at Beta Group, and (b) decide whether a model could replace manual HR reviews. "
            "Which one calls for an explanatory model and which calls for a predictive model, "
            "and why does the distinction matter for how you build each one? What about the "
            "bias vs variance concerns between the two models?"
        ),
        "model_answer": (
            "Task (a) — the fairness audit — is explanatory: Sophia wants to understand whether "
            "age and gender affect promotion, so she cares about the coefficients and their "
            "interpretation, not predicting individual outcomes. Task (b) — automating HR review "
            "— is predictive: she cares whether predictions are accurate and cost-effective. "
            "The distinction matters because you build them differently: explanatory models "
            "favor interpretability (simple specification, judged on whether coefficients are "
            "unbiased and sensible); predictive models favor performance (potentially complex "
            "models judged on out-of-sample accuracy or dollar return). "
            "On bias vs variance: for the explanatory model, bias is the real enemy — a biased "
            "gender coefficient (e.g., from omitted variables) makes the fairness conclusion "
            "wrong regardless of fit, so we accept higher variance for unbiased coefficients. "
            "For the predictive model, it's the opposite: we care about total error (bias² + "
            "variance), and will use more complex models that may be biased in individual "
            "coefficients but predict better out of sample."
        ),
        "rubric": rubric(
            full=(
                "Identifies (a) as explanatory and (b) as predictive (by name or description), "
                "AND explains why the distinction matters (understanding coefficients vs "
                "accurate predictions), AND addresses bias/variance in a recognizable way "
                "(e.g., 'can't afford a wrong coefficient even with less stability' for (a), "
                "'care about overall prediction error' for (b)). Plain language counts."
            ),
            partial=(
                "Labels the two tasks correctly AND clearly explains why it matters, BUT "
                "bias/variance discussion is shallow or missing — OR bias/variance is good but "
                "the task distinction is vague."
            ),
            minimal=(
                "Identifies only the task types OR only the bias-variance framing, not both."
            ),
            none=(
                "Swaps the tasks with no coherent reason, OR fails to address the distinction."
            ),
        ),
        "common_wrong_answers": (
            "- Calling (a) predictive because 'we're trying to predict if age affects promotion' "
            "— this confuses prediction of the outcome with inference about coefficients.\n"
            "- Saying 'predictive models have more bias, explanatory models have more variance' "
            "without explanation reverses the concern. A student who explains it clearly in "
            "plain language ('we can't risk the coefficient being wrong even if it means less "
            "precise estimates') should get full credit even without the words bias/variance; "
            "a student who drops the words without understanding should not."
        ),
    },
    {
        "order_index": 1,
        "points": 4,
        "question_text": (
            "In Part B, dropping `avg_training_score` from the regression changed the coefficient "
            "on `gender`. What does this tell us about the original coefficient on `gender`, and "
            "why should Sophia care? Use the phrase 'holding all else constant' in your answer."
        ),
        "model_answer": (
            "The fact that the gender coefficient changed when `avg_training_score` was dropped "
            "means the original coefficient was absorbing some of the effect of training score — "
            "not because gender genuinely matters that way, but because gender and training "
            "score are correlated in the data. Sophia should care because the simple correlation "
            "between gender and promotion is not the same as gender's independent effect. Only "
            "when we hold `avg_training_score` constant (and other relevant factors) do we see "
            "gender's effect 'all else equal' — which is what a fairness audit actually needs."
        ),
        "rubric": rubric(
            full=(
                "Recognizes that the original coefficient was capturing something that wasn't "
                "purely gender (any phrasing — 'inflated', 'absorbing', 'picking up training "
                "score's effect', 'overestimating', etc.) AND explains why this matters for the "
                "audit: the raw gender–promotion relationship can't be trusted because other "
                "factors are entangled with it."
            ),
            partial=(
                "Notices the coefficient changed and identifies that training score and gender "
                "are related, BUT doesn't clearly explain why controlling matters for Sophia's "
                "question."
            ),
            minimal="Just says 'the coefficient changed, so one of them is important' without the entanglement logic.",
            none="Claims the change is random or meaningless, or that we should keep both coefficients as-is.",
        ),
        "common_wrong_answers": (
            "'It shows avg_training_score is more important than gender' — misses the point. The "
            "issue isn't which is more important; removing a relevant variable distorts the "
            "coefficient of the one that's left in."
        ),
    },
    {
        "order_index": 2,
        "points": 4,
        "question_text": (
            "A colleague wants to use 0.5 as the cutoff for the promotion model 'because that's "
            "what the library defaults to.' What hidden assumption about costs is built into a "
            "0.5 cutoff, and why is that assumption wrong for Sophia?"
        ),
        "model_answer": (
            "A 0.5 cutoff implicitly assumes that a false positive and a false negative are "
            "equally costly — if they weren't, 0.5 wouldn't maximize expected return. In Sophia's "
            "case, an FN costs $1,000 and an FP costs $500: the two errors are not equally bad. "
            "A false denial is twice as costly as a false promotion, so the optimal cutoff "
            "should be lower than 0.5 — we should be willing to predict 'promote' with less "
            "confidence, because missing a real promotion hurts more than wrongly promoting "
            "someone."
        ),
        "rubric": rubric(
            full=(
                "Recognizes that 0.5 treats FP and FN as equally bad (any wording — 'treating "
                "both mistakes the same', 'assuming they're interchangeable') AND explains why "
                "that doesn't fit Sophia's costs (FN > FP) AND correctly concludes the optimal "
                "cutoff should be lower than 0.5."
            ),
            partial=(
                "Identifies the equal-treatment assumption but doesn't connect it to Sophia's "
                "numbers, OR connects it but gets the direction of the shift wrong."
            ),
            minimal="Vaguely says '0.5 is not optimal because costs differ' without the mechanism.",
            none="Claims 0.5 is fine, or says the cutoff depends on something unrelated to cost.",
        ),
        "common_wrong_answers": (
            "'0.5 should be higher because we want to be more careful' reverses the logic. If FN "
            "costs more, you want more predictions of 'promote', which means a lower cutoff."
        ),
    },
    {
        "order_index": 3,
        "points": 4,
        "question_text": (
            "In Part C5, when the cost of a false denial (FN) dropped from $1,000 to $400, the "
            "optimal cutoff moved higher. Explain why a lower FN cost leads to a higher cutoff. "
            "(This is not a memory question — work through the logic.)"
        ),
        "model_answer": (
            "When FN cost drops from $1,000 to $400, false denials become less painful. We no "
            "longer need to lean so hard toward predicting 'promote' to avoid FNs — we can "
            "afford to be more selective. A higher cutoff means we only predict 'promote' when "
            "the model is more confident, which produces fewer FPs at the cost of more FNs. "
            "Since each FN now hurts less, that trade is favorable. So a lower FN cost shifts "
            "the optimal cutoff upward."
        ),
        "rubric": rubric(
            full=(
                "Explains that lowering FN cost makes missed promotions less painful (any "
                "wording) AND explains that a higher cutoff = being more selective / more "
                "confident before predicting 'promote', producing more missed positives but "
                "fewer wrong promotions, AND correctly connects these to conclude the optimal "
                "cutoff rises."
            ),
            partial=(
                "Gets the direction right and vaguely connects it to cost, but the trade-off "
                "between the two error types isn't clearly explained."
            ),
            minimal="States the direction without mechanism, OR explains a mechanism but gets the direction wrong.",
            none="'The cutoff went up because the cost went down' with no reasoning.",
        ),
        "common_wrong_answers": (
            "'When FN cost drops, we care less about FNs so we should have a lower cutoff' "
            "conflates 'caring less about FNs' with 'being less careful overall'. Caring less "
            "about missed promotions means we can afford to make more of them, which means we "
            "can be more restrictive about predicting 'promote' (higher cutoff)."
        ),
    },
    {
        "order_index": 4,
        "points": 4,
        "question_text": (
            "In the Classification HW you tuned two Decision Tree hyperparameters: "
            "`min_samples_split` and `max_depth`. For each one: (a) what does it control about "
            "how the tree is built? (b) If you make it more restrictive (larger "
            "`min_samples_split`, or smaller `max_depth`), what happens to the tree, and why "
            "does that change the risk of overfitting vs underfitting? Be specific about the "
            "mechanism — not just that it affects overfitting, but how."
        ),
        "model_answer": (
            "`min_samples_split` sets the minimum number of data points a node must contain "
            "before the tree is allowed to split it further. If a node has fewer points than "
            "this threshold, the tree leaves it alone and makes it a leaf. Increasing "
            "`min_samples_split` makes the tree more conservative — it only splits where "
            "there's substantial evidence (lots of points), so it won't chase small, noisy "
            "sub-groups. That reduces overfitting. Pushed too high, the tree becomes so "
            "restricted that it misses real patterns and underfits.\n\n"
            "`max_depth` sets the maximum number of levels (cuts from root down to a leaf) the "
            "tree is allowed to have. Decreasing `max_depth` limits how many cuts the tree can "
            "make, producing a simpler tree that can't memorize every wiggle in the training "
            "data — this reduces overfitting. A very small `max_depth` makes the tree too "
            "shallow to capture real structure, leading to underfitting. A larger `max_depth` "
            "lets the tree keep splitting, fitting training noise and overfitting.\n\n"
            "Both knobs control model complexity. Making them more restrictive (higher "
            "`min_samples_split`, lower `max_depth`) simplifies the tree: less overfitting, "
            "risk of underfitting if pushed too far. Making them less restrictive allows a "
            "more complex tree that's more prone to overfit."
        ),
        "rubric": rubric(
            full=(
                "For BOTH hyperparameters: correctly explains the control mechanism "
                "(`min_samples_split` = minimum data points required before a split is allowed "
                "/ won't split tiny groups; `max_depth` = maximum levels / number of cuts from "
                "root to leaf), AND explains the mechanism linking it to over/underfit (e.g., "
                "'higher min_samples_split prevents the tree from splitting on small noisy "
                "subgroups so it can't memorize quirks', 'lower max_depth limits the number of "
                "cuts so the tree is too simple to chase every training-set wiggle'), AND "
                "correctly identifies direction for both. Plain language counts."
            ),
            partial=(
                "Both hyperparameters addressed with correct mechanism + direction, but one "
                "mechanism explanation is shallow (e.g., 'min_samples_split prevents "
                "overfitting by being stricter' without explaining WHY strictness helps)."
            ),
            minimal=(
                "States 'both control overfitting' or 'both limit complexity' without "
                "explaining the mechanism or direction; OR only one hyperparameter discussed "
                "meaningfully."
            ),
            none=(
                "Reverses direction (claims higher `min_samples_split` or larger `max_depth` "
                "reduces overfitting), doesn't address over/underfitting at all, or conflates "
                "with unrelated hyperparameters (`n_estimators`, `max_features`)."
            ),
        ),
        "common_wrong_answers": (
            "'They control overfitting.' The central trap — no mechanism, no direction. "
            "Minimal (1) at best, don't let articulate phrasing push it higher.\n"
            "'They make the tree smaller / less complex.' Correct but mechanism-free — does "
            "not explain HOW a smaller tree prevents memorization. Partial at best.\n"
            "Reversing direction (larger `min_samples_split` → more splits; smaller "
            "`max_depth` → more overfitting). Zero.\n"
            "Only addresses overfitting, ignores underfitting. Trade-off is part of the answer "
            "— partial.\n"
            "Confuses with Random Forest knobs (`n_estimators`, `max_features`). Off-topic."
        ),
    },
]


def main():
    # Login
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]
    print(f"Logged in as: {resp['user']['name']}")

    due = (datetime.utcnow() + timedelta(days=7)).isoformat()

    quiz_payload = {
        "course_id": COURSE_ID,
        "title": "BADM 576 — Classification HW Quiz",
        "description": (
            "Short-answer quiz on the big ideas from the Classification HW. "
            "5 questions, 4 points each, 20 points total. Answer in your own words — "
            "a one-sentence-and-done answer will not get full credit, explain why. "
            "This quiz score multiplies your Classification HW grade. "
            "Your answers will first be graded by an AI grader and then reviewed by the instructor."
        ),
        "max_attempts": 3,
        "time_limit_minutes": 10,
        "due_date": due,
        "is_active": True,
        "show_answers_after_submit": False,
        "require_all_questions": True,
        "use_llm_grader": True,
        "llm_grader_model": "claude-opus-4-7",
        "grading_instructions": GRADING_INSTRUCTIONS,
        "hw_reference": HW_REFERENCE,
        "questions": [
            {
                "question_type": "short_answer",
                "question_text": q["question_text"],
                "correct_answer": "instructor_review",
                "points": q["points"],
                "order_index": q["order_index"],
                "rubric": q["rubric"],
                "model_answer": q["model_answer"],
                "common_wrong_answers": q["common_wrong_answers"],
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
    print(f"LLM Grader: {quiz_payload['llm_grader_model']}")
    print()
    print(f"Students: http://3.90.88.174:3002/quizzes")
    print(f"Instructor: http://3.90.88.174:3002/instructor/quizzes")


if __name__ == "__main__":
    main()
