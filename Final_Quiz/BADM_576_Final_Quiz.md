# BADM 576 Quiz

**Data Science and Analytics · Spring 2026**

**Total: 100 points · Time: 60 minutes**

---

## Instructions

This quiz has three sections:

- **Section A — Multiple Choice** (20 questions, 2 points each, 40 points total)
- **Section B — Short Answer** (10 questions, 4 points each, 40 points total)
- **Section C — Scenarios** (4 questions, 5 points each, 20 points total)

For multiple choice, select one option. For short answers, 1 to 3 sentences is enough; longer answers do not earn extra credit. For scenarios, 2 to 4 sentences with clear reasoning. The quiz is open-notes. Manage your time: roughly 20 minutes for Section A, 25 for Section B, and 15 for Section C.

---

## Section A — Multiple Choice (40 points)

Two points each. Select the best answer.

---

**1.** If the JobMatch platform reports a hire rate of 1.8%, what does this number describe?

a) The probability that any given recruiter will hire a candidate today
b) The platform-level rate aggregated across all applications
c) The probability that any given candidate will be hired
d) The recruiter's success rate on a typical day

---

**2.** "The unit of observation" refers to:

a) The dataset's total size
b) What one row of the data represents
c) The variable being predicted
d) The number of features in the model

---

**3.** In Rajasi's loan story, why does the model become progressively more biased over time?

a) The bank deliberately programs bias into the model
b) The economy changes and customers change with it
c) Outcomes can only be observed for approved applicants, so the training data shrinks toward what the model already favored
d) Loan officers override the model's recommendations

---

**4.** "Selection bias" most accurately means:

a) The analyst chose the wrong variables to include
b) The model selected the wrong cutoff
c) The data only includes those who showed up and got measured, not the full population of interest
d) The training/test split was done incorrectly

---

**5.** In the car-price example, the regression coefficient on age went from +1,147 (alone) to −1,730 (with car type added). What does this teach us?

a) The original data was wrong
b) Linear regression cannot handle car prices
c) Coefficient values depend on what other variables are in the model
d) Car type is the only variable that matters

---

**6.** In the Berkeley admissions example, the aggregate admit rates were 45% for men and 30% for women. When broken down by department, women had higher admit rates in every department. What is this called?

a) Sample selection bias
b) Simpson's paradox
c) Survivorship bias
d) The curse of dimensionality

---

**7.** Three things the notes describe as "three forms of one insight" are:

a) Mean, median, and mode
b) Bias, variance, and noise
c) Simpson's paradox, the regression sign-flip, and controlling for confounders
d) Precision, recall, and accuracy

---

**8.** The unifying lesson behind Berkeley admissions, the cars sign-flip, and the HR promotion case is:

a) Bigger samples always give better answers
b) The level at which you look at the data determines what pattern appears
c) Categorical variables should always be excluded
d) Aggregate data is more reliable than disaggregated data

---

**9.** Bias is best described as:

a) Random fluctuation in predictions across different samples
b) A systematic underestimation or overestimation of an effect that more data will not fix
c) Rounding error in a coefficient
d) An analyst's personal preference for one variable

---

**10.** In the average-of-three-numbers example, a student who learns "the answer is the middle number" will:

a) Have low bias and low variance
b) Have low bias on the original example but high variance on new questions
c) Have high bias on the original example
d) Always get the right answer

---

**11.** Adding more data to a model with omitted-variable bias will:

a) Fix the bias by reducing the standard error
b) Make the bias worse
c) Not fix the bias, because the bias is in the specification, not the sample size
d) Eventually fix the bias if the dataset is large enough

---

**12.** Explanatory work primarily fights ____, predictive work primarily fights ____.

a) noise; signal
b) variance; bias
c) bias; variance
d) sampling error; measurement error

---

**13.** In the cricket auction example, "celebrity appeal" was constructed as:

a) A column in the player database
b) The fitted value from regressing price on on-field statistics
c) The residual after regressing price on on-field statistics
d) The average of social-media followers and brand deals

---

**14.** According to the notes, a residual is best described as:

a) Garbage to be discarded
b) The error term that always disappears in a good model
c) The size of our ignorance, expressed in the same units as the thing we were trying to predict
d) A bug in the regression algorithm

---

**15.** Frisch-Waugh / partialling out tells us that a multiple regression coefficient on X is equivalent to:

a) The simple correlation between X and Y
b) The simple regression of (Y residualized on other variables) on (X residualized on other variables)
c) The mean of X divided by the mean of Y
d) The variance of X times the covariance of Y

---

**16.** In the churn-prediction example, customer C-103 had P(churn) = 0.42. At threshold 0.50 they were classified "will not churn"; at threshold 0.30 they were classified "will churn." This shows:

a) The model's prediction is unreliable
b) Where to set the threshold is a business decision about the cost of each kind of mistake
c) The model needs more training data
d) Probabilities below 0.5 are meaningless

---

**17.** For a COVID test deployed at an airport vs. a hospital, the ideal threshold is likely:

a) The same in both places, because the test is the same
b) Different, because the cost of false positives and false negatives differs by setting
c) Always 0.5 by convention
d) Higher in the hospital because hospitals see more cases

---

**18.** Recall measures:

a) Of the things I picked, how many were good
b) Of all the good things that could have happened, how many did I miss
c) The proportion of true negatives in the data
d) Total accuracy across all classes

---

**19.** As you add more and more features to a dataset:

a) The model always becomes more accurate
b) Every observation eventually becomes unique and "similar to this one" loses meaning
c) The training error always decreases and the test error always decreases too
d) You always need more data, but the relationships stay the same

---

**20.** PCA, embeddings, and matrix factorization are all responses to:

a) Missing data
b) Categorical variables
c) The problem that high-dimensional data has no useful sense of "similar"
d) Overfitting in decision trees

---

## Section B — Short Answer (40 points)

Four points each. One to three sentences is sufficient.

---

**21.** Define "unit of observation" in your own words, and give one example of how the same dataset could support two different units of observation. *(4 points)*

> _Your answer:_

---

**22.** Explain in 2 to 3 sentences why a bank that retrains its loan model only on outcomes of previously-approved applicants will become progressively biased over time, even if no one ever programmed bias into the system. *(4 points)*

> _Your answer:_

---

**23.** In your own words, what is the single underlying lesson connecting Simpson's paradox, the regression sign-flip, and "controlling for" a confounder? *(4 points)*

> _Your answer:_

---

**24.** In the HR promotion example, the gender coefficient looks negative in a simple model but vanishes when training score is included. Explain in 2 to 3 sentences what this means for the diagnosis "there is gender bias in promotions." *(4 points)*

> _Your answer:_

---

**25.** What is the key difference between bias and variance, and why are they NOT interchangeable problems? Give one fix for each. *(4 points)*

> _Your answer:_

---

**26.** In the average-of-three-numbers example, three rules ("sum and divide," "the middle number," "the count of numbers") all produced the answer 3 for the input {2, 3, 4}. Why is this a good metaphor for overfitting? *(4 points)*

> _Your answer:_

---

**27.** In the cricket auction example, what was "celebrity appeal" before the regression, and what was it after? Explain how the regression made it observable. *(4 points)*

> _Your answer:_

---

**28.** A model with 0.92 AUC deployed at threshold 0.5 may produce more harm than the same model deployed at threshold 0.7. Explain why, in 2 to 3 sentences. *(4 points)*

> _Your answer:_

---

**29.** When would you prefer high recall over high precision, and when the reverse? Give one concrete business example for each. *(4 points)*

> _Your answer:_

---

**30.** Explain why adding more and more features to a customer dataset eventually makes "who is similar to this customer" an unanswerable question. What is the technical name for this phenomenon? *(4 points)*

> _Your answer:_

---

## Section C — Scenarios (20 points)

Five points each. Two to four sentences with clear reasoning.

---

**31.** *(5 points)* A product manager reports: "Our recommendation engine has 73% accuracy across the platform. We should ship it." A recruiter responds: "But on the engineering jobs I work on, I see it recommend the wrong candidate three times out of four." Both could be right at the same time. Explain why, and what one piece of additional information you would request before deciding whether to ship.

> _Your answer:_

---

**32.** *(5 points)* A hospital reports that patients treated by Doctor A have a 90% survival rate while patients treated by Doctor B have a 75% survival rate. Hospital leadership is about to reassign all critical cases away from Doctor B. Before they do, what would you ask, and what is the specific risk you are guarding against?

> _Your answer:_

---

**33.** *(5 points)* A team's hiring model is performing poorly in production. The lead data scientist proposes collecting another 50,000 resumes to retrain on. A junior team member asks: "What if the problem is that we never recorded years of relevant work experience as a separate field?" Whose intuition is more likely correct, and why?

> _Your answer:_

---

**34.** *(5 points)* A bank's fraud-detection model is set at threshold 0.5. Every false positive costs the bank about $20 in customer-service time to resolve. Every false negative (a real fraud that goes through) costs the bank an average of $800. Should the bank's threshold be higher than 0.5, lower than 0.5, or exactly 0.5? Explain your reasoning in 2 to 3 sentences.

> _Your answer:_

---

*End of quiz. Please review your answers before submitting.*
