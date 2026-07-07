"""Create the BADM 576 Final Quiz on the live server.

100 points across three sections:
  - Section A: 20 MCQs (2 pts each, 40 pts) — auto-graded
  - Section B: 10 short-answer (4 pts each, 40 pts) — LLM-graded with rubrics
  - Section C: 4 scenarios (5 pts each, 20 pts) — LLM-graded with rubrics

60-min timer, 1 attempt, require all questions, hide answers after submit.
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


def rubric_4pt(full, partial, minimal, none_):
    return [
        {"label": "full", "points": 4, "criteria": full},
        {"label": "partial", "points": 3, "criteria": "Strong but missing a piece: " + partial},
        {"label": "partial-low", "points": 2, "criteria": "Partially on track: " + partial},
        {"label": "minimal", "points": 1, "criteria": minimal},
        {"label": "none", "points": 0, "criteria": none_},
    ]


def rubric_5pt(full, strong, partial, minimal, none_):
    return [
        {"label": "full", "points": 5, "criteria": full},
        {"label": "strong", "points": 4, "criteria": strong},
        {"label": "partial", "points": 3, "criteria": partial},
        {"label": "partial-low", "points": 2, "criteria": "Partially on track: " + partial},
        {"label": "minimal", "points": 1, "criteria": minimal},
        {"label": "none", "points": 0, "criteria": none_},
    ]


GRADING_INSTRUCTIONS = (
    "This is the BADM 576 final quiz, covering the big ideas from the course: unit of "
    "observation, selection bias, same-data-different-conclusion, bias vs variance, "
    "residuals, classification metrics & thresholds, dimensionality / PCA, and recommendation "
    "systems & fairness. Reward understanding expressed in plain language; if a student "
    "describes the right concept in their own words, give full credit even without technical "
    "terms. When a student uses technical terms, look for evidence they understand what the "
    "terms mean and credit the understanding, not the vocabulary alone. Partial credit is "
    "expected and appropriate. For Section B (short answer, 4 pts), use the 2+2 rubric: 2 pts "
    "for the correct concept, 2 pts for clear elaboration or a concrete example. For Section C "
    "(scenarios, 5 pts), reward the analytical move (naming the right concept and asking the "
    "right diagnostic question / proposing a sensible remedy) even if the final recommendation "
    "differs from the expected answer, as long as the reasoning is sound."
)

HW_REFERENCE = (
    "This quiz covers the entire BADM 576 course. Recurring examples students saw across the "
    "term: JobMatch (hiring platform — unit of observation, selection bias), Beta Group "
    "promotion / Classification HW (logistic regression, gender coefficient, cutoff tuning), "
    "Berkeley admissions (Simpson's paradox), the soccer / cricket auction (residuals as "
    "celebrity appeal), the 388-cars and movie-reviews datasets (PCA), Spotify / Netflix "
    "(recommender systems and the four conditions). The class explicitly de-emphasized "
    "memorizing names like 'Frisch-Waugh' — credit plain-language equivalents. Plain-language "
    "translations the grader should accept: 'omitted variable bias' / 'confounding' → "
    "'picking up something else', 'absorbing another variable's effect'; 'selection bias' → "
    "'training only on the survivors of an earlier filter'; 'curse of dimensionality' → "
    "'every observation becomes unique', 'distances flatten'; 'closed-loop / popularity loop' "
    "→ 'rich-get-richer feedback', 'the model only sees what it surfaced'."
)


# ---------------------------------------------------------------------------
# SECTION A — MULTIPLE CHOICE (20 questions × 2 pts = 40 pts)
# ---------------------------------------------------------------------------

MCQ_QUESTIONS = [
    {
        "question_text": (
            "A dashboard shows JobMatch's overall hire rate is 1.8%. A recruiter screening 12 "
            "applications today asks why that number isn't useful to her. The best answer is:"
        ),
        "options": [
            "The 1.8% covers thousands of decisions, not her twelve",
            "The dashboard hasn't been updated recently",
            "Aggregate rates always need to be seasonally adjusted",
            "Twelve applications is too small a sample for any rate",
        ],
        "correct_answer": "The 1.8% covers thousands of decisions, not her twelve",
    },
    {
        "question_text": (
            "A bank retrains its loan model each year using only the outcomes of loans it "
            "approved. Over several years, why does the model get more biased?"
        ),
        "options": [
            "Macroeconomic conditions inevitably shift",
            "Models lose statistical power as they age",
            "Training data narrows toward the applicants the model already favored",
            "Loan officers override more of the decisions each year",
        ],
        "correct_answer": "Training data narrows toward the applicants the model already favored",
    },
    {
        "question_text": (
            "A hiring model is trained only on candidates who passed an initial resume screen. "
            "The most important caveat about its predictions is that:"
        ),
        "options": [
            "The training set is too small to be reliable",
            "The features are not predictive enough",
            "It only describes candidates who already passed the screen",
            "Resumes are too noisy as input data",
        ],
        "correct_answer": "It only describes candidates who already passed the screen",
    },
    {
        "question_text": (
            "A regression of car price on age gives +1,147. After adding car type, the same "
            "coefficient becomes -1,730. This is best understood as:"
        ),
        "options": [
            "An error in how the data was recorded",
            "Linear models breaking down on car prices",
            "Model variance — a coefficient changing with the model specification",
            "Model bias — a coefficient changing with the model specification",
        ],
        "correct_answer": "Model bias — a coefficient changing with the model specification",
    },
    {
        "question_text": (
            "A graduate program admits 45% of men and 30% of women overall. By department, "
            "every department admits women at a higher rate than men. This is best explained by:"
        ),
        "options": [
            "Survivorship bias in the application data",
            "Inconsistent admission criteria across departments",
            "An error somewhere in the aggregate numbers",
            "Women applying more to harder-to-enter departments",
        ],
        "correct_answer": "Women applying more to harder-to-enter departments",
    },
    {
        "question_text": (
            "In a multiple regression, \"controlling for age\" effectively does what?"
        ),
        "options": [
            "Holds age fixed at its mean for predictions",
            "Removes the part of all variables explained by age",
            "Forces the age coefficient to be statistically significant",
            "Includes age but ignores its coefficient",
        ],
        "correct_answer": "Removes the part of all variables explained by age",
    },
    {
        "question_text": "Which most clearly distinguishes bias from variance?",
        "options": [
            "Bias comes from the data; variance comes from the model",
            "Bias is what you get; variance is what you should have gotten",
            "Bias is a specification problem; variance is sample sensitivity",
            "Bias means underfit; variance means overfit, in every situation",
        ],
        "correct_answer": "Bias is a specification problem; variance is sample sensitivity",
    },
    {
        "question_text": (
            "A team's regression gives wrong-signed coefficients. They propose collecting more "
            "data. This will most likely:"
        ),
        "options": [
            "Not help, because the issue is in the model specification",
            "Fix the issue, given enough additional rows",
            "Help only if they sample stratified by treatment",
            "Help slowly as variance shrinks toward the true value",
        ],
        "correct_answer": "Not help, because the issue is in the model specification",
    },
    {
        "question_text": (
            "A model achieves 92% accuracy on the training set and 64% accuracy on the test "
            "set. The most likely problem is:"
        ),
        "options": [
            "High bias",
            "Selection bias in the training set",
            "Wrong loss function for the problem",
            "High variance",
        ],
        "correct_answer": "High variance",
    },
    {
        "question_text": (
            "A different model achieves 65% accuracy on the training set and 64% accuracy on "
            "the test set. The most likely problem is:"
        ),
        "options": [
            "High bias",
            "High variance",
            "Wrong loss function for the problem",
            "Selection bias in the training set",
        ],
        "correct_answer": "High bias",
    },
    {
        "question_text": (
            "A soccer club is auctioning players. Auction prices are presumably driven by two "
            "things: a player's measurable on-field statistics, and an unmeasurable \"celebrity "
            "appeal\" (brand value, fan following, social-media presence). An analyst regresses "
            "auction price on on-field statistics. To get a measurement of celebrity appeal, "
            "she should use:"
        ),
        "options": [
            "The intercept of the regression",
            "The residual from the regression",
            "The R-squared of the regression",
            "The fitted value from the regression",
        ],
        "correct_answer": "The residual from the regression",
    },
    {
        "question_text": (
            "A classifier outputs P(churn) = 0.42 for a customer. Whether to flag this "
            "customer for retention depends on:"
        ),
        "options": [
            "Whether 0.42 is closer to 0 than to 1",
            "The model's overall accuracy score",
            "The variance of the prediction itself",
            "The threshold the business has chosen",
        ],
        "correct_answer": "The threshold the business has chosen",
    },
    {
        "question_text": (
            "A bank's fraud model has AUC 0.92. To decide between threshold 0.3 and 0.7, the "
            "team should:"
        ),
        "options": [
            "Pick whichever threshold maximizes the AUC value",
            "Weigh the costs of false positives vs. false negatives",
            "Default to 0.5 since that is the standard convention",
            "Use the threshold that yields exactly 50% precision",
        ],
        "correct_answer": "Weigh the costs of false positives vs. false negatives",
    },
    {
        "question_text": (
            "Of the customers your model flagged as likely to churn, only 60% actually "
            "churned. This 60% is the model's:"
        ),
        "options": ["Recall", "Accuracy", "Specificity", "Precision"],
        "correct_answer": "Precision",
    },
    {
        "question_text": (
            "Of the customers who actually churned, your model flagged only 40%. This 40% is "
            "the model's:"
        ),
        "options": ["Specificity", "Precision", "Recall", "Accuracy"],
        "correct_answer": "Recall",
    },
    {
        "question_text": (
            "A retail analyst adds 20 new features to her customer dataset, hoping it will "
            "help her find customers similar to a target customer. To her surprise, the \"find "
            "similar customers\" results get worse, not better. The most likely reason is:"
        ),
        "options": [
            "The notion of \"similar\" weakens as dimensions grow",
            "The new features introduce multicollinearity",
            "Training data should grow with the number of features",
            "The features must have been categorical",
        ],
        "correct_answer": "The notion of \"similar\" weakens as dimensions grow",
    },
    {
        "question_text": (
            "PCA reduces a high-dimensional dataset to a few \"principal components.\" These "
            "components are best understood as:"
        ),
        "options": [
            "The original features, ranked by importance",
            "Categorical labels assigned to each row",
            "New axes capturing the most variation in the data",
            "The errors of a regression model",
        ],
        "correct_answer": "New axes capturing the most variation in the data",
    },
    {
        "question_text": (
            "A streaming service applies matrix factorization to its (users x movies) ratings "
            "matrix. The \"latent factors\" it discovers most likely represent:"
        ),
        "options": [
            "Movies that all users rated the same way",
            "Underlying dimensions of taste shared across users and movies",
            "Hidden errors in the ratings data",
            "Demographic groupings of users",
        ],
        "correct_answer": "Underlying dimensions of taste shared across users and movies",
    },
    {
        "question_text": (
            "Of these four products, which is the WORST fit for a recommender-system framing "
            "(and is best handled as classification)?"
        ),
        "options": [
            "Spotify song recommendations",
            "Loan approval at a bank",
            "Netflix movie suggestions",
            "YouTube short videos",
        ],
        "correct_answer": "Loan approval at a bank",
    },
    {
        "question_text": (
            "A hiring model uses no race, gender, or age fields. Why might we still want to "
            "audit it for fairness?"
        ),
        "options": [
            "Other features can serve as proxies for protected ones",
            "Models without protected attributes can still be illegal",
            "AUC scores routinely hide unfair behavior",
            "Aggregate accuracy metrics tend to overstate true accuracy",
        ],
        "correct_answer": "Other features can serve as proxies for protected ones",
    },
]


# ---------------------------------------------------------------------------
# SECTION B — SHORT ANSWER (10 questions × 4 pts = 40 pts)
# ---------------------------------------------------------------------------

SHORT_ANSWER_QUESTIONS = [
    {
        "question_text": (
            "Define \"unit of observation\" in your own words, and give one example of how the "
            "same dataset could support two different units of observation."
        ),
        "model_answer": (
            "Unit of observation = what one row of the data represents. Example: in JobMatch "
            "events.csv one row is a single event (click, application, offer); the same dataset "
            "can be analyzed at the event level, the candidate level (events grouped by "
            "candidate), or the job level (events grouped by job). Each gives different answers."
        ),
        "rubric": rubric_4pt(
            full=(
                "Defines unit of observation as what one row represents (any clear wording — "
                "'what each row stands for', 'the level of analysis') AND gives a concrete "
                "example of two different units derivable from the same dataset (event vs "
                "candidate, transaction vs customer, click vs session, etc.)."
            ),
            partial=(
                "Definition is correct, but the example is vague or only names one unit; OR "
                "two units are named but the definition is shaky."
            ),
            minimal=(
                "Mentions 'rows' or 'level' without clearly tying it to what one row represents, "
                "and the example is missing or wrong."
            ),
            none_=(
                "Confuses unit of observation with sample size, variable, or feature; or doesn't "
                "address either the definition or the example."
            ),
        ),
        "common_wrong_answers": (
            "'Unit of observation is the sample size' — confuses unit with N. "
            "'Unit of observation is what variable you're predicting' — confuses unit with target."
        ),
    },
    {
        "question_text": (
            "Explain in 2 to 3 sentences why a bank that retrains its loan model only on "
            "outcomes of previously-approved applicants becomes progressively biased over "
            "time, even if no one ever programs bias into the system."
        ),
        "model_answer": (
            "The bank can observe repayment outcomes only for approved applicants; rejected "
            "applicants have no observable outcome and are dropped from training. Over "
            "successive retrains, training data narrows toward the kind of applicant the model "
            "already favored. The model becomes more confident on a smaller slice and "
            "progressively blinder to the rest. No one programmed bias; the selection mechanism "
            "produced it."
        ),
        "rubric": rubric_4pt(
            full=(
                "Identifies the feedback loop (only approved applicants generate outcomes, so "
                "rejected applicants drop from training data) AND explains the consequence "
                "(training data narrows toward the model's existing preferences, bias compounds, "
                "no one designed it). Plain language counts."
            ),
            partial=(
                "Names the feedback loop but doesn't explain the compounding consequence; OR "
                "describes the consequence but is vague about the mechanism."
            ),
            minimal=(
                "Says 'the data is biased' without explaining the selection mechanism, OR says "
                "'the model gets worse' without identifying why."
            ),
            none_=(
                "Attributes the bias to programming choices, model architecture, or unrelated "
                "causes (drift, sample size, etc.)."
            ),
        ),
        "common_wrong_answers": (
            "'The model becomes biased because the world changes' — that's drift, not the "
            "selection-feedback mechanism. "
            "'Adding more data fixes it' — no, more biased data makes it worse."
        ),
    },
    {
        "question_text": (
            "In your own words, what is the single underlying lesson connecting Simpson's "
            "paradox, the regression sign-flip, and \"controlling for\" a confounder?"
        ),
        "model_answer": (
            "The conclusion you reach depends on what else is in the model — equivalently, on "
            "what level you analyze the data at. Aggregating up (Simpson's), disaggregating "
            "down, and conditioning on a third variable (controlling for) are three forms of "
            "the same operation. The level at which you look determines what pattern appears."
        ),
        "rubric": rubric_4pt(
            full=(
                "Identifies the core insight (the answer depends on what's in the model / what "
                "level you analyze at) AND recognizes that all three are facets of one operation. "
                "Plain language equivalents like 'the same data tells different stories depending "
                "on which other variables you include' get full credit."
            ),
            partial=(
                "Captures the 'depends on the model' insight but doesn't unify all three "
                "phenomena; OR mentions all three but doesn't articulate the underlying "
                "operation."
            ),
            minimal=(
                "Treats them as three unrelated tricks or just defines one of them."
            ),
            none_=(
                "Says 'always control for everything' or 'the more variables the better' — "
                "misses the conditional-on-spec nature of the lesson."
            ),
        ),
        "common_wrong_answers": (
            "'Always control for confounders' — the lesson is more subtle: the answer is "
            "always conditional on the specification, not that one specification is correct."
        ),
    },
    {
        "question_text": (
            "In an HR promotion analysis, the gender coefficient looks negative in a simple "
            "model but vanishes when training-attendance is included. Explain in 2 to 3 "
            "sentences what this means for the diagnosis \"there is gender bias in promotions.\""
        ),
        "model_answer": (
            "The aggregate gap is real but it is mediated by training attendance, not gender "
            "per se. Within any training-attendance band, men and women are promoted at the "
            "same rate. The diagnosis shifts from \"promotion bias\" to \"training-attendance "
            "gap\" — completely different remedies. The fix is no longer at the promotion "
            "decision; it is at whatever upstream process drives the difference in attendance."
        ),
        "rubric": rubric_4pt(
            full=(
                "Identifies that the gender effect is mediated by (or absorbed by) training "
                "attendance — promotions don't depend on gender once attendance is held fixed — "
                "AND notes the diagnostic / remedy shift (the problem isn't at the promotion "
                "decision; it's upstream in whatever drives attendance differences)."
            ),
            partial=(
                "Notes that the gap disappears once attendance is in the model but doesn't "
                "explain what that means for the diagnosis or remedy."
            ),
            minimal=(
                "Says 'training matters more than gender' without engaging with the diagnosis."
            ),
            none_=(
                "Concludes that bias is definitely present, OR concludes that bias is definitely "
                "absent — neither follows. The point is that the location of the bias has "
                "shifted."
            ),
        ),
        "common_wrong_answers": (
            "'There is no bias' — wrong. The gap is real; it just isn't at the promotion step. "
            "Bias may live upstream in attendance access. "
            "'Therefore gender doesn't matter' — same error."
        ),
    },
    {
        "question_text": (
            "What is the key difference between bias and variance, and why are they NOT "
            "interchangeable problems? Give one fix for each."
        ),
        "model_answer": (
            "Bias = systematic error from a wrong model specification (e.g., omitted variable). "
            "Fix: include the right variables, re-specify the model. Variance = sensitivity to "
            "the particular sample (predictions change as data changes). Fix: regularization, "
            "more data, simpler models. They look the same on a single error metric but have "
            "different causes and different remedies."
        ),
        "rubric": rubric_4pt(
            full=(
                "Defines bias as a specification / systematic error (any clear wording — "
                "'wrong model', 'missing the right variables') AND defines variance as "
                "sample-sensitivity (any clear wording — 'wiggles with the data', 'overfitting "
                "to the sample') AND offers one correct fix for each (bias: re-specify / add "
                "variables; variance: more data, regularization, simpler model)."
            ),
            partial=(
                "Definitions correct but only one fix is given; OR both fixes given but one "
                "definition is shaky."
            ),
            minimal=(
                "Names bias and variance but conflates them or only gives one fix that applies "
                "to both."
            ),
            none_=(
                "Reverses the definitions, OR proposes 'collect more data' as the fix for bias."
            ),
        ),
        "common_wrong_answers": (
            "'More data fixes both' — no, more data does not fix omitted-variable bias. "
            "'Variance is from the data, bias is from the model' — too coarse; bias is a "
            "specification problem, variance is sample sensitivity."
        ),
    },
    {
        "question_text": (
            "Explain why fitting a training example perfectly is not enough to know whether a "
            "model has learned the underlying pattern. What does this have to do with the "
            "train/test split?"
        ),
        "model_answer": (
            "Multiple rules can fit the same training example; from training accuracy alone "
            "you can't tell whether a model learned the general pattern or coincidentally "
            "memorized a rule that fits the example. Only a new test point reveals which is "
            "which. That gap is exactly what train/test splits are designed to expose."
        ),
        "rubric": rubric_4pt(
            full=(
                "Notes that many different rules can fit the same training data (memorization "
                "vs generalization, any plain-language equivalent like 'the model could be "
                "memorizing rather than learning the pattern') AND connects this to the "
                "purpose of the test set: a held-out sample is the actual evaluation because "
                "only new data exposes whether the rule generalizes."
            ),
            partial=(
                "Notes that training accuracy alone isn't enough but doesn't articulate why "
                "(multiple-rules-fit-the-same-data); OR mentions overfitting without tying it "
                "to the train/test split."
            ),
            minimal=(
                "Just says 'we need a test set' without explaining what it tests for."
            ),
            none_=(
                "Claims training accuracy is sufficient, or that the train/test split is a "
                "sample-size technique."
            ),
        ),
        "common_wrong_answers": (
            "'Train/test splits are about having enough data' — no, they are about evaluating "
            "whether learned rules generalize."
        ),
    },
    {
        "question_text": (
            "A residual is what is left over after a regression has explained as much as it "
            "can. Explain in 2 to 3 sentences why residuals are sometimes more interesting "
            "than the regression coefficients themselves. Give one example."
        ),
        "model_answer": (
            "Residuals capture what the model could not explain. Sometimes that \"unexplained\" "
            "portion is the actual variable of interest — something not directly measurable but "
            "constructible by subtracting away the explainable part. Example: in a soccer-player "
            "auction, regress price on on-field stats; the residual measures celebrity appeal — "
            "a variable that did not exist as a column in any database until the regression "
            "constructed it. Residuals make unmeasurable things measurable."
        ),
        "rubric": rubric_4pt(
            full=(
                "Conceptual point: residuals can be the variable of interest (not garbage / not "
                "noise); the unexplained part is sometimes what we're after AND a clear concrete "
                "example demonstrating 'construct an unmeasurable from observed patterns' "
                "(soccer/cricket auction celebrity appeal, or any analogous example like "
                "teacher value-added, store-manager skill, etc.)."
            ),
            partial=(
                "Conceptual point is present but the example is vague or generic ('residuals "
                "tell you about errors')."
            ),
            minimal=(
                "Defines residuals as 'leftover error' without engaging with why they're useful."
            ),
            none_=(
                "Treats residuals as model failure to be eliminated, OR confuses them with "
                "outliers."
            ),
        ),
        "common_wrong_answers": (
            "'Residuals are noise; we want them to be small' — true mechanically but misses "
            "the point. The unexplained portion can carry signal we want to measure."
        ),
    },
    {
        "question_text": (
            "When would you prefer high recall over high precision, and when the reverse? "
            "Give one concrete business example for each."
        ),
        "model_answer": (
            "High recall when missing a positive is very costly: cancer screening, fraud on "
            "large transactions, security/safety alerts. High precision when a false positive "
            "is very costly: flagging a customer as fraudulent (loses their trust), expensive "
            "interventions on people who don't need them."
        ),
        "rubric": rubric_4pt(
            full=(
                "Frames each correctly: high recall = high cost-of-miss (false negative is "
                "expensive); high precision = high cost-of-false-alarm (false positive is "
                "expensive) AND gives a plausible concrete example for each side (cancer "
                "screening / fraud / safety alerts for recall; trust-damaging or expensive "
                "interventions for precision)."
            ),
            partial=(
                "Framing correct but only one side has a clear example, OR examples present "
                "but the framing of which is which is muddled."
            ),
            minimal=(
                "Defines recall and precision but doesn't connect them to when each matters."
            ),
            none_=(
                "Reverses the trade-off (e.g., recommends high precision for cancer screening) "
                "or claims the two are interchangeable."
            ),
        ),
        "common_wrong_answers": (
            "'High recall is always better because we want to catch everything' — wrong. In a "
            "trust-damaging context (false-fraud flags), precision matters more."
        ),
    },
    {
        "question_text": (
            "Explain why adding more and more features to a customer dataset eventually makes "
            "\"who is similar to this customer\" an unanswerable question. What is this problem "
            "called?"
        ),
        "model_answer": (
            "As dimensions grow, every observation becomes unique on the joint distribution; "
            "distance between any two points approaches a similar value, so \"nearest neighbor\" "
            "loses discriminating power. This is the curse of dimensionality. Compression "
            "techniques (PCA, embeddings) recover useful similarity by finding the few "
            "dimensions that carry the structure."
        ),
        "rubric": rubric_4pt(
            full=(
                "Mechanism: as features grow, every observation becomes unique / distances "
                "between any two points flatten, so 'nearest neighbor' or 'similar' loses "
                "meaning AND names the curse of dimensionality."
            ),
            partial=(
                "Mechanism described but the name is missing; OR the name is given but the "
                "mechanism is shaky."
            ),
            minimal=(
                "Just says 'too many features' or 'overfitting' without the distance-flattening "
                "intuition."
            ),
            none_=(
                "Confuses with multicollinearity, sample-size issues, or noise."
            ),
        ),
        "common_wrong_answers": (
            "'Multicollinearity' — different concept (correlated features, not flattened "
            "distances). "
            "'You need more data' — even with infinite data, distances still flatten."
        ),
    },
    {
        "question_text": (
            "Spotify works well as a recommender system, but a bank's loan-approval system "
            "would be a poor fit for the same approach. Name two of the conditions Spotify "
            "satisfies that loan approval does not."
        ),
        "model_answer": (
            "Any two of: (1) Latent taste — Spotify users have unmeasurable preferences not "
            "captured by song features alone; loan repayment is largely explained by observable "
            "features (income, credit history). (2) Dense interactions — Spotify users have "
            "streamed many songs; a loan applicant has only one application. (3) Vast catalog "
            "— Spotify has millions of tracks; loan products are a handful. (4) Cheap mistakes "
            "— a bad Spotify recommendation costs a skip; a bad loan decision costs the "
            "applicant their housing or the bank a default."
        ),
        "rubric": rubric_4pt(
            full=(
                "Names two of the four conditions (latent taste, dense interactions, vast "
                "catalog, cheap mistakes) AND explains for each why Spotify satisfies it but "
                "loans don't. Plain-language naming is fine ('lots of songs vs few loan "
                "products', 'a song skip is cheap vs a loan default is expensive')."
            ),
            partial=(
                "Names two conditions but only justifies one with a Spotify-vs-loan contrast; "
                "OR justifies both but the second condition overlaps with the first."
            ),
            minimal=(
                "Names one condition with justification, or names two without explaining why "
                "the contrast holds."
            ),
            none_=(
                "Confuses recommender failure modes with classification failure modes; or "
                "discusses unrelated factors like 'loans are more regulated'."
            ),
        ),
        "common_wrong_answers": (
            "'Loans are regulated and Spotify isn't' — true but unrelated to the technical fit. "
            "Don't credit unless paired with a real condition."
        ),
    },
]


# ---------------------------------------------------------------------------
# SECTION C — SCENARIOS (4 questions × 5 pts = 20 pts)
# ---------------------------------------------------------------------------

SCENARIO_QUESTIONS = [
    {
        "question_text": (
            "A product manager reports: \"Our recommendation engine has 73% accuracy across "
            "the platform. We should ship it.\" A recruiter responds: \"But on the engineering "
            "jobs I work on, I see it recommend the wrong candidate three times out of four.\" "
            "Both could be right at the same time. Explain why, and what one piece of "
            "additional information you would request before deciding whether to ship."
        ),
        "model_answer": (
            "The 73% is at the platform unit of analysis; the recruiter's experience is at a "
            "subgroup unit (engineering jobs). Both can be true simultaneously when performance "
            "is uneven across subgroups. Before shipping, request performance broken down by "
            "job category (or seniority, or recruiter, or any meaningful subgroup). The right "
            "decision metric matches the unit at which the action is taken."
        ),
        "rubric": rubric_5pt(
            full=(
                "Names the unit-of-analysis mismatch (any clear wording — 'aggregate vs "
                "subgroup', 'overall vs job-category-specific') AND requests a specific kind of "
                "subgroup performance breakdown (by job category, seniority, recruiter, etc.) "
                "AND clearly connects this to the decision (the action is taken at the subgroup "
                "level so the metric should be too)."
            ),
            strong=(
                "Names the mismatch and requests subgroup performance, but the connection to "
                "the decision is left implicit."
            ),
            partial=(
                "Notes that 'subgroups can differ' but doesn't articulate the unit-of-analysis "
                "framing or the right diagnostic question."
            ),
            minimal=(
                "Just says 'check performance by group' without explaining why or naming the "
                "underlying issue."
            ),
            none_=(
                "Concludes one of them must be wrong, or that the 73% is the relevant metric. "
                "Misses that both can be true at different units."
            ),
        ),
        "common_wrong_answers": (
            "'The recruiter has a small sample size, the 73% is more reliable' — misses the "
            "unit-of-analysis insight. The 73% can be perfectly accurate at the platform level "
            "while being useless to a recruiter."
        ),
    },
    {
        "question_text": (
            "A hospital reports that patients treated by Doctor A have a 90% survival rate, "
            "while patients treated by Doctor B have a 75% survival rate. Hospital leadership "
            "is about to reassign all critical cases away from Doctor B. Before they do, what "
            "would you ask, and what is the specific risk you are guarding against?"
        ),
        "model_answer": (
            "Ask for survival rates broken down by case severity. Doctor B may be receiving "
            "the harder cases — in which case the aggregate is misleading and B may actually "
            "be performing better than A on equivalent severity. This is Simpson's paradox; "
            "the diagnostic move is to break the data into groups (case mix) before drawing "
            "the conclusion. Reassigning critical cases away from B without this check could "
            "remove the best critical-case doctor."
        ),
        "rubric": rubric_5pt(
            full=(
                "Names Simpson's paradox or describes the underlying mechanism in plain "
                "language (aggregate can reverse once you condition on case severity) AND "
                "asks the right diagnostic question (survival rates broken down by case "
                "severity / case mix) AND notes the risk: reassigning critical cases away "
                "from B could remove the best critical-case doctor."
            ),
            strong=(
                "Asks for the case-severity breakdown and explains the mechanism, but doesn't "
                "explicitly state the consequence of getting it wrong."
            ),
            partial=(
                "Asks 'are the cases comparable?' or similar without articulating Simpson's "
                "paradox or the case-mix mechanism."
            ),
            minimal=(
                "Just says 'we need more data' or 'the survey could be biased' without the "
                "case-mix insight."
            ),
            none_=(
                "Endorses the reassignment, or attributes the gap to randomness with no "
                "diagnostic move."
            ),
        ),
        "common_wrong_answers": (
            "'Maybe B is just a worse doctor; the data speaks for itself' — misses the "
            "case-mix confound. "
            "'Sample size' — possible but not the central risk."
        ),
    },
    {
        "question_text": (
            "A bank's fraud-detection model is set at threshold 0.5. Every false positive "
            "costs the bank about $20 in customer-service time to resolve. Every false "
            "negative (a real fraud that goes through) costs the bank an average of $800. "
            "Should the bank's threshold be higher than 0.5, lower than 0.5, or exactly 0.5? "
            "Explain your reasoning in 2 to 3 sentences."
        ),
        "model_answer": (
            "Lower than 0.5. False negatives are 40x more costly than false positives, so the "
            "bank should be willing to flag more cases (higher recall) at the cost of more "
            "false alarms. The threshold operationalizes the cost asymmetry; it is not a "
            "statistical default. (Bonus: breakeven occurs at P > 20/800 = 0.025, so the "
            "optimal threshold is around 0.025 — far below 0.5.)"
        ),
        "rubric": rubric_5pt(
            full=(
                "Correctly answers 'lower than 0.5' AND explains the cost asymmetry (FN $800 "
                "is 40x more expensive than FP $20, so the bank should flag more aggressively) "
                "AND clear reasoning that connects threshold to cost. Bonus credit (still capped "
                "at 5) for computing breakeven (~0.025)."
            ),
            strong=(
                "Correctly answers 'lower' and explains cost asymmetry, but reasoning is "
                "abbreviated or doesn't tie threshold to action."
            ),
            partial=(
                "Says 'lower' without clearly explaining why, OR explains cost asymmetry but "
                "concludes 'higher' or 'depends'."
            ),
            minimal=(
                "Mentions costs differ without committing to a direction."
            ),
            none_=(
                "Says 'higher than 0.5' (reversed direction), or 'exactly 0.5 because that's "
                "standard'. Reversed direction zeros out unless the rest of the reasoning "
                "salvages partial credit."
            ),
        ),
        "common_wrong_answers": (
            "'Higher than 0.5 because we want to be more careful' — reverses the trade-off. "
            "Higher threshold = fewer flags = more FNs through. Wrong direction. "
            "'Exactly 0.5 because that's the math default' — exactly the trap."
        ),
    },
    {
        "question_text": (
            "A music streaming service runs a recommender that learns from user listening "
            "history. After six months, the team notices that newer or unusual songs almost "
            "never get recommended, while a small set of popular tracks dominate everyone's "
            "feed. The model still scores well on standard metrics. Explain in 2 to 4 "
            "sentences what mechanism is most likely producing this pattern, and one thing the "
            "team could do about it."
        ),
        "model_answer": (
            "This is a popularity loop (a closed-loop failure mode). Items the model surfaces "
            "get more interactions, which makes them rank higher, which makes them surfaced "
            "more. The rich get richer; the long tail starves. Standard precision metrics look "
            "fine because the model is doing well on the items it surfaces and is silent about "
            "the items it does not. Mitigation: monitor coverage (not just precision), or "
            "inject exploration slots that deliberately surface items outside the user's "
            "history."
        ),
        "rubric": rubric_5pt(
            full=(
                "Identifies the closed-loop / popularity-loop mechanism (any clear wording — "
                "'rich get richer', 'the model only sees what it surfaced', 'feedback loop "
                "where popular gets more popular') AND explains why standard metrics still "
                "look good (the model is evaluated on items it surfaces, and is silent on the "
                "long tail) AND names a reasonable mitigation (coverage monitoring, "
                "exploration / epsilon-greedy slots, diversity injection, randomized recs)."
            ),
            strong=(
                "Names the mechanism and one mitigation but doesn't explain why metrics still "
                "look good."
            ),
            partial=(
                "Vaguely describes a feedback effect but doesn't articulate the closed-loop "
                "mechanism, OR misses the mitigation."
            ),
            minimal=(
                "Says 'popular songs get recommended more' without the loop / metric blindspot "
                "insight."
            ),
            none_=(
                "Attributes the pattern to the model architecture (e.g., 'collaborative "
                "filtering can't handle new items') with no feedback-loop reasoning, OR "
                "concludes the model is fine."
            ),
        ),
        "common_wrong_answers": (
            "'It's a cold-start problem for new songs' — partially related but misses the "
            "self-reinforcing loop on existing popular items. "
            "'The metrics are wrong' — closer but doesn't explain why they look fine while the "
            "behavior is bad."
        ),
    },
]


# ---------------------------------------------------------------------------
# Build payload
# ---------------------------------------------------------------------------

def build_questions():
    out = []
    order = 0

    # Section A — MCQ, 2 pts each
    for q in MCQ_QUESTIONS:
        out.append({
            "question_type": "mcq",
            "question_text": q["question_text"],
            "options": q["options"],
            "correct_answer": q["correct_answer"],
            "points": 2,
            "order_index": order,
        })
        order += 1

    # Section B — short_answer, 4 pts each
    for q in SHORT_ANSWER_QUESTIONS:
        out.append({
            "question_type": "short_answer",
            "question_text": q["question_text"],
            "correct_answer": "instructor_review",
            "points": 4,
            "order_index": order,
            "rubric": q["rubric"],
            "model_answer": q["model_answer"],
            "common_wrong_answers": q["common_wrong_answers"],
        })
        order += 1

    # Section C — short_answer, 5 pts each
    for q in SCENARIO_QUESTIONS:
        out.append({
            "question_type": "short_answer",
            "question_text": q["question_text"],
            "correct_answer": "instructor_review",
            "points": 5,
            "order_index": order,
            "rubric": q["rubric"],
            "model_answer": q["model_answer"],
            "common_wrong_answers": q["common_wrong_answers"],
        })
        order += 1

    return out


def main():
    resp = api_call("POST", "/api/v1/auth/login", {
        "email": "instructor@stakeholdersim.edu",
        "password": "instructor123",
    })
    token = resp["access_token"]
    print(f"Logged in as: {resp['user']['name']}")

    questions = build_questions()
    total_points = sum(q["points"] for q in questions)
    print(f"Built {len(questions)} questions, {total_points} total points.")
    assert total_points == 100, f"Expected 100 points, got {total_points}"
    assert len(questions) == 34, f"Expected 34 questions, got {len(questions)}"

    due = (datetime.utcnow() + timedelta(days=7)).isoformat()

    quiz_payload = {
        "course_id": COURSE_ID,
        "title": "BADM 576 — Final Quiz",
        "description": (
            "Final quiz for BADM 576 (Data Science and Analytics, Spring 2026). "
            "100 points across three sections: 20 multiple choice (2 pts each), "
            "10 short answer (4 pts each), and 4 scenarios (5 pts each). "
            "60 minutes, ONE attempt only. Open-notes. The quiz screen locks once "
            "you start — leaving the tab repeatedly will auto-submit your work. "
            "Manage your time: about 20 min for Section A, 25 min for Section B, "
            "15 min for Section C. Short-answer and scenario responses are graded "
            "by an AI grader with instructor review; final scores are released "
            "after that review."
        ),
        "max_attempts": 1,
        "time_limit_minutes": 60,
        "due_date": due,
        "is_active": True,
        "show_answers_after_submit": False,
        "require_all_questions": True,
        "use_llm_grader": True,
        "llm_grader_model": "claude-opus-4-7",
        "grading_instructions": GRADING_INSTRUCTIONS,
        "hw_reference": HW_REFERENCE,
        "questions": questions,
    }

    quiz = api_call("POST", "/api/v1/quizzes", quiz_payload, token)

    print()
    print("=" * 60)
    print("FINAL QUIZ CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Quiz ID:      {quiz['id']}")
    print(f"Title:        {quiz['title']}")
    print(f"Questions:    {quiz['question_count']}")
    print(f"Total Points: {quiz['total_points']}")
    print(f"Due:          {due}")
    print(f"Time limit:   60 minutes")
    print(f"Attempts:     1")
    print(f"LLM Grader:   {quiz_payload['llm_grader_model']}")
    print()
    print(f"Students:     http://3.90.88.174:3002/quizzes")
    print(f"Take quiz:    http://3.90.88.174:3002/quizzes/{quiz['id']}")
    print(f"Instructor:   http://3.90.88.174:3002/instructor/quizzes/{quiz['id']}/results")


if __name__ == "__main__":
    main()
