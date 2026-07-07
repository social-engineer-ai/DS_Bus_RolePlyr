# BADM 576 — HW3 Quiz (Session 5, April 22)

**Time:** 10 minutes &nbsp;·&nbsp; **Questions:** 5 &nbsp;·&nbsp; **Total:** 20 points &nbsp;·&nbsp; **Format:** short answer (2–3 sentences per question)

This quiz checks whether you understood the *big ideas* from HW3 — not whether you remember the code or exact numbers. Answer in your own words. A one-sentence-and-done answer will not get full credit; explain *why*.

---

## Question 1 (4 points) — Two jobs, two modelsSophia gave us two problems: (a) figure out whether age or gender affects promotion at Beta Group, and (b) decide whether a model could replace manual HR reviews. Which one calls for an **explanatory** model and which calls for a **predictive** model, and why does the distinction matter for how you build each one? What about the **bias vs variance** concerns between the two models?

---

## Question 2 (4 points) — The coefficient that moved

In Part B, dropping `avg_training_score` from the regression changed the coefficient on `gender`. What does this tell us about the original coefficient on `gender`, and why should Sophia care? Use the phrase "holding all else constant" in your answer.

---

## Question 3 (4 points) — Why 0.5 is not the default it looks like

A colleague wants to use 0.5 as the cutoff for the promotion model "because that's what the library defaults to." What **hidden assumption** about costs is built into a 0.5 cutoff, and why is that assumption wrong for Sophia?

---

## Question 4 (4 points) — The direction the cutoff moved

In Part C5, when the cost of a false denial (FN) dropped from $1,000 to $400, the optimal cutoff moved **higher**. Explain why a *lower* FN cost leads to a *higher* cutoff. (This is not a memory question — work through the logic.)

---

## Question 5 (4 points) — Why one-at-a-time tuning can mislead

In Part E, you picked the best value for each Decision Tree hyperparameter *independently*, then combined them into a "naive combo." The grid-search winner was usually a different configuration. What does this tell us about how hyperparameters behave, and what is the general lesson for anyone tuning a model?

---

---

# ANSWER KEY & RUBRIC (not for students)

## Question 1 — Explanatory vs predictive

**Model answer.** Task (a) — the fairness audit — is explanatory: Sophia wants to understand *whether* age and gender affect promotion, so she cares about the *coefficients* and their interpretation, not about predicting individual outcomes. Task (b) — automating HR review — is predictive: Sophia doesn't care *why* the model predicts what it does, she cares whether the predictions are *accurate and cost-effective*. The distinction matters because you build and evaluate them differently: explanatory models favor interpretability (e.g., logistic regression with carefully chosen controls, judged on whether coefficients make sense and are unbiased), while predictive models favor performance (potentially more complex models judged on out-of-sample accuracy or dollar return).

On **bias vs variance**: for the explanatory model, bias is the real enemy — if the coefficient on gender is biased (say, because of omitted variables), the fairness conclusion is wrong regardless of how well the model fits. We're willing to accept higher variance (less stable estimates) in exchange for unbiased coefficients, which is why we use a simple, interpretable specification and worry about confounding. For the predictive model, it's the opposite: we care about total error (bias² + variance) because that's what determines prediction quality. We'll happily use a more complex model — biased in its individual coefficients but lower total error — if it predicts better out of sample. So the two tasks have nearly opposite tolerances for the same trade-off.

**Rubric (4 pts)** — *credit the underlying idea even if the student doesn't use the exact terms "bias," "variance," or "explanatory/predictive." If they describe the right concept in plain language, that counts.*
- **Full credit (4):** correctly identifies (a) as explanatory-style and (b) as predictive-style (by name or by description) AND explains *why* the distinction matters in terms of what you optimize for (understanding coefficients vs accurate predictions) AND addresses bias/variance in a recognizable way — e.g., "for the fairness audit, we can't afford the coefficient to be off even if we lose some stability; for the deployment model, we care about overall prediction error and can use more complex models."
- **Partial (2–3):** correctly labels the two tasks AND the "why it matters" is clear, BUT the bias-variance discussion is shallow or missing, OR the bias-variance discussion is good but the task distinction is vague.
- **Minimal (1):** correctly identifies only the task types OR only the bias-variance framing, not both.
- **No credit (0):** swaps the tasks with no coherent reason, OR doesn't address the distinction at all.

**Common wrong answer to watch for:**
- Calling Task (a) predictive because "we're trying to predict if age affects promotion." This confuses prediction (predicting the outcome variable) with inference about coefficients.
- Saying "predictive models have more bias, explanatory models have more variance" with no further explanation — this has the flavor right but reverses the actual concern. A student who explains it clearly in plain language ("we can't risk the coefficient being wrong even if it means less precise estimates") should get full credit even without the words bias/variance; a student who drops the words without understanding should not.

---

## Question 2 — The coefficient that moved (omitted variable bias)

**Model answer.** The fact that the gender coefficient changed when `avg_training_score` was dropped means the *original* coefficient was absorbing some of the effect of training score — not because gender genuinely matters that way, but because gender and training score are correlated in the data. Sophia should care because it means the simple correlation between gender and promotion is *not* the same as gender's independent effect. Only when we hold `avg_training_score` constant (and other relevant factors) do we see gender's effect on promotion "all else equal." This is what a fairness audit actually needs.

**Rubric (4 pts)** — *credit the underlying idea even if the student doesn't use "confounding," "omitted variable bias," or "holding all else constant." Terms like "overestimating," "picking up," "overlapping with," "mixing together" all capture the core concept.*
- **Full credit (4):** recognizes that the original coefficient was capturing something that wasn't purely gender (phrased any way — "inflated," "absorbing," "picking up training score's effect," "overestimating gender's role," etc.) AND explains why this matters for the audit — we can't trust the raw relationship between gender and promotion because other factors are entangled with it.
- **Partial (2–3):** notices that the coefficient changed and correctly identifies that training score and gender are related, BUT doesn't clearly explain why controlling matters for answering Sophia's question.
- **Minimal (1):** just says "the coefficient changed, so one of them is important" without the entanglement logic.
- **No credit (0):** claims the change is random, meaningless, or that we should keep both coefficients as-is.

**Common wrong answer to watch for:** "It shows `avg_training_score` is more important than gender" — this misses the point. The issue isn't which is more important; it's that removing a relevant variable distorts the coefficient of the one that's left in.

---

## Question 3 — The 0.5 cutoff trap

**Model answer.** A 0.5 cutoff implicitly assumes that a false positive and a false negative are **equally costly** — if they weren't, 0.5 wouldn't be the point that maximizes expected return. In Sophia's case, an FN costs $1,000 and an FP costs $500: the two errors are not equally bad. A false denial (FN) is twice as costly as a false promotion (FP), so the optimal cutoff should be *lower* than 0.5 — we should be willing to predict "promote" with less confidence, because missing a real promotion hurts more than wrongly promoting someone.

**Rubric (4 pts)** — *credit plain-language reasoning. Students may not say "equal costs" but may say "treating both mistakes the same," "assuming FN and FP are interchangeable," etc.*
- **Full credit (4):** recognizes that 0.5 treats FP and FN as equally bad (in any wording) AND explains why that doesn't fit Sophia's situation (FN costs more) AND correctly concludes the optimal cutoff should be *lower* than 0.5.
- **Partial (2–3):** identifies the equal-treatment assumption but doesn't connect it to Sophia's cost numbers, OR connects it but gets the direction of the shift wrong.
- **Minimal (1):** vaguely says "0.5 is not optimal because costs differ" without explaining the mechanism.
- **No credit (0):** claims 0.5 is fine, or says the cutoff depends on something unrelated to cost (e.g., accuracy alone).

**Common wrong answer to watch for:** saying "0.5 should be higher because we want to be more careful" — this reverses the logic. If FN costs more, you want *more* predictions of "promote," which means a *lower* cutoff, not higher.

---

## Question 4 — Direction of the cutoff shift

**Model answer.** When FN cost drops from $1,000 to $400, false denials become *less* painful. That means we no longer need to lean so hard toward predicting "promote" to avoid FNs — we can afford to be more selective. A higher cutoff means we only predict "promote" when the model is more confident, which produces *fewer* FPs at the cost of *more* FNs. Since each FN now hurts less, that trade is now favorable. So a lower FN cost shifts the optimal cutoff upward.

**Rubric (4 pts)** — *students don't need the exact words "false positive," "false negative," or "trade-off." "Missed promotion," "wrong promotion," "being strict vs lenient" all work if the logic is right.*
- **Full credit (4):** explains that lowering FN cost makes missed promotions less painful (any wording), AND explains that a higher cutoff means being more selective / more confident before promoting, which produces more missed positives but fewer wrong promotions, AND correctly connects these to conclude the optimal cutoff rises.
- **Partial (2–3):** gets the direction right and vaguely connects it to cost, but the trade-off between the two error types isn't clearly explained.
- **Minimal (1):** states the direction without any mechanism, OR explains a mechanism but gets the direction wrong.
- **No credit (0):** "the cutoff went up because the cost went down" with no reasoning connecting the two.

**Common wrong answer to watch for:** "When FN cost drops, we care less about FNs so we should have *lower* cutoff." This conflates "caring less about FNs" with "being less careful overall." In fact, caring less about missed promotions means we can afford to make *more* of them, which means we can be *more* restrictive about predicting "promote" (higher cutoff).

---

## Question 5 — Hyperparameters interact

**Model answer.** Picking each hyperparameter's best value independently assumes they don't interact — that the best `max_depth` is the same regardless of what `min_samples_leaf` is. But hyperparameters often interact: `max_depth` and `min_samples_leaf` both control tree complexity, so the best `max_depth` depends on what `min_samples_leaf` you've set, and vice versa. The general lesson: when choices in a model are not independent, you cannot optimize them one at a time — you have to search over combinations. This applies beyond hyperparameters to any case where the right value of one parameter depends on another (feature engineering choices, regularization, etc.).

**Rubric (4 pts)** — *students don't need the term "interaction" or "independence." "Depend on each other," "don't work in isolation," "affect each other," "related," etc., all count.*
- **Full credit (4):** explains that one-at-a-time tuning assumes hyperparameters don't affect each other (any wording), AND gives some plausible reason why they might (e.g., both controlling tree depth/complexity, or one constrains what the other can do), AND generalizes to a broader lesson — you need to search combinations when choices are interrelated.
- **Partial (2–3):** gets the "they aren't independent" idea but doesn't explain *why* they interact, OR explains interaction but doesn't generalize.
- **Minimal (1):** says "they should be tuned together" without explaining why.
- **No credit (0):** claims naive tuning is fine, or blames randomness or the specific data rather than the tuning approach.

**Common wrong answer to watch for:** "The naive combo was wrong because we didn't try enough values." This misses the point — the issue isn't the coarseness of the grid, it's the assumption that each hyperparameter's best value is fixed regardless of the others.

---

---

## Scoring summary

| Q | Topic | Points |
|---|-------|--------|
| 1 | Explanatory vs predictive | 4 |
| 2 | Omitted variable bias | 4 |
| 3 | The 0.5 cutoff trap | 4 |
| 4 | Direction of cutoff shift | 4 |
| 5 | Hyperparameter interaction | 4 |
| | **Total** | **20** |

## For your AI grader

**Global grading principle.** This quiz tests whether students grasped the *big ideas*, not whether they memorized terminology. If a student describes the correct concept in plain language — even without using technical terms like "bias," "variance," "confounding," "omitted variable bias," "hyperparameter interaction," "false positive/false negative," etc. — award full credit. Conversely, if a student drops the right technical term without showing they understand what it means, do not reward the term alone.

Examples of plain-language equivalents that should earn full credit:
- "confounding" / "omitted variable bias" → "the coefficient was picking up something else," "gender and training were mixed together," "removing training made gender absorb its effect"
- "false negative" / "false positive" → "missed promotions," "wrong promotions," "promoting someone who shouldn't be promoted"
- "hyperparameter interaction" → "they affect each other," "the best value of one depends on the other," "they don't work in isolation"
- "bias vs variance" → "how wrong the model is on average vs how much it wiggles," "being consistently off vs being all over the place"

**Logistics.** Pass each student's answer along with the model answer and rubric for that question. Grade each question independently — do not let the rubric for Q1 leak into Q2. The "common wrong answer" notes are to help the grader avoid being tricked by fluent-sounding but incorrect reasoning (this shows up especially in Q3 and Q4, where the direction of the argument is easy to get backwards).
