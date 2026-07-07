"""Create the BADM 576 Week 7 ML Process Exercise on the live server."""

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

# Step 1: Create Persona
persona = api_call("POST", "/api/v1/personas", {
    "course_id": COURSE_ID,
    "name": "Dr. Analytics",
    "title": "ML Process Instructor",
    "background": (
        "You are a business analytics professor who teaches the machine learning pipeline. "
        "You present business scenarios and guide students through applying the 7-step ML process: "
        "Task definition, Data/Experience, Model building, Loss function, Gradient descent, "
        "Inference, and Drift analysis."
    ),
    "personality": (
        "Socratic and probing. You never give answers directly \u2014 you ask follow-up questions "
        "to check understanding. When a student gives a correct but surface-level answer, you push "
        "for deeper reasoning. When they make a mistake, you ask a question that helps them see "
        "the error. You are encouraging but rigorous."
    ),
    "concerns": [
        "Task definition precision",
        "Outcome variable choice",
        "Predictor selection and leakage",
        "Loss function choice and business asymmetry",
        "Gradient descent understanding",
        "Inference computation",
        "Data and concept drift",
    ],
    "required_questions": [
        "Is this a regression or classification problem and why?",
        "What is your outcome variable and what are the predictors?",
        "Are there any data quality or leakage concerns?",
        "Should the loss function be symmetric or asymmetric and why?",
        "What real-world change could cause your model to drift?",
    ],
}, token)
print(f"PERSONA created: {persona['id']} - {persona['name']}")

# Step 2: Create Rubric
rubric = api_call("POST", "/api/v1/rubrics", {
    "course_id": COURSE_ID,
    "name": "ML Process Exercise Rubric",
    "criteria": [
        {
            "name": "task_definition",
            "display_name": "Task Definition (T)",
            "description": (
                "Can the student precisely define what the machine is learning to do? "
                "Identifies regression vs classification, specifies the prediction target, unit, and timing."
            ),
            "max_points": 15,
            "scoring_guide": {
                "15": "Correctly identifies regression, specifies outcome precisely (annual medical costs for a new policyholder at enrollment), explains why",
                "10": "Identifies regression and outcome but lacks precision on unit or timing",
                "5": "Vague or partially incorrect task definition",
                "0": "Cannot define the task or confuses regression with classification",
            },
        },
        {
            "name": "data_experience",
            "display_name": "Data / Experience (E)",
            "description": (
                "Can the student identify the outcome variable, select appropriate predictors, "
                "and recognize data quality issues (completeness, accuracy, recency, coverage, leakage)?"
            ),
            "max_points": 20,
            "scoring_guide": {
                "20": "Correctly identifies Y (annual charges), lists relevant predictors available at enrollment, discusses at least 2 data quality concerns, identifies leakage risks",
                "15": "Identifies Y and predictors correctly but limited data quality discussion",
                "10": "Partially correct \u2014 misses key predictors or includes leaky features",
                "5": "Significant confusion about outcome vs predictors or ignores data quality",
                "0": "Cannot identify the outcome variable",
            },
        },
        {
            "name": "model_building",
            "display_name": "Model Building",
            "description": (
                "Can the student write the linear regression equation with appropriate predictors "
                "and state the expected sign of each beta coefficient?"
            ),
            "max_points": 15,
            "scoring_guide": {
                "15": "Writes correct equation form, includes relevant predictors, correctly states expected sign of each beta with reasoning",
                "10": "Correct equation form and most signs correct but reasoning is thin",
                "5": "Attempts the equation but has sign errors or missing predictors",
                "0": "Cannot write the model equation",
            },
        },
        {
            "name": "loss_function",
            "display_name": "Loss Function (P)",
            "description": (
                "Does the student understand SSE/RMSE? Can they reason about whether symmetric or "
                "asymmetric loss is appropriate for this business problem?"
            ),
            "max_points": 15,
            "scoring_guide": {
                "15": "Explains SSE/RMSE clearly, makes well-reasoned argument for asymmetric loss with business impact reasoning",
                "10": "Understands SSE/RMSE but asymmetric reasoning is shallow",
                "5": "Basic understanding of loss but cannot reason about asymmetry",
                "0": "Does not understand what a loss function measures",
            },
        },
        {
            "name": "gradient_descent",
            "display_name": "Gradient Descent",
            "description": (
                "Can the student explain conceptually how gradient descent finds the optimal parameters? "
                "Understanding of learning rate, convergence, and why exhaustive search is impractical."
            ),
            "max_points": 10,
            "scoring_guide": {
                "10": "Clear conceptual explanation: iterative downhill movement on loss surface, role of learning rate, why exhaustive search fails",
                "7": "Understands the iterative idea but vague on learning rate or convergence",
                "3": "Memorized definition without real understanding",
                "0": "Cannot explain gradient descent",
            },
        },
        {
            "name": "inference",
            "display_name": "Inference / Prediction",
            "description": (
                "Given learned betas and a new observation, can the student correctly compute "
                "a predicted value and interpret the coefficients?"
            ),
            "max_points": 10,
            "scoring_guide": {
                "10": "Correctly plugs values into the equation, computes the prediction, and interprets at least 2 betas in business terms",
                "7": "Correct computation but limited interpretation",
                "3": "Attempts computation but makes arithmetic or conceptual errors",
                "0": "Cannot perform inference",
            },
        },
        {
            "name": "drift_analysis",
            "display_name": "Drift Analysis",
            "description": (
                "Can the student identify realistic scenarios that would cause the model to degrade? "
                "Distinguishes data drift from concept drift."
            ),
            "max_points": 15,
            "scoring_guide": {
                "15": "Identifies specific, realistic drift scenarios (e.g., pandemic, new treatments, policy changes), correctly distinguishes data drift from concept drift",
                "10": "Identifies drift scenarios but does not distinguish data vs concept drift",
                "5": "Vague or generic answer about drift",
                "0": "Does not understand model drift",
            },
        },
    ],
}, token)
print(f"RUBRIC created: {rubric['id']} - {rubric['name']} ({rubric['total_points']} pts)")

# Step 3: Create Scenario
scenario_desc = (
    "You are conducting an in-class exercise for BADM 576 (Data Science and Analytics). "
    "Present the student with the following business scenario, then walk them through the "
    "7-step ML process by asking questions one step at a time.\n\n"
    "BUSINESS SCENARIO TO PRESENT:\n"
    "HealthPredict is a health insurance company that wants to predict annual medical costs "
    "for new policyholders at enrollment time. They have 5 years of claims data including "
    "policyholder age, BMI, smoking status, number of dependents, region, and the total "
    "annual medical charges billed. Accurate predictions help them set premiums fairly \u2014 "
    "overpricing loses customers to competitors, underpricing means the company loses money "
    "on high-cost policyholders.\n\n"
    "EXERCISE FLOW:\n"
    "1. Start by presenting the HealthPredict scenario clearly to the student. Describe the "
    "business context and what the company wants to accomplish.\n"
    "2. Ask the student to define the Task (T) \u2014 what is being predicted? Is it regression "
    "or classification? Why?\n"
    "3. Ask about the Data (E) \u2014 what is the outcome variable? What are good predictors "
    "available at enrollment time? Any data quality concerns or leakage risks?\n"
    "4. Ask them to sketch the Model \u2014 write a linear regression equation with the predictors, "
    "state the expected sign of each beta coefficient and explain why\n"
    "5. Ask about the Loss Function (P) \u2014 SSE/RMSE or asymmetric? Ask them to reason about "
    "which prediction error is costlier for this specific business: overestimating costs or "
    "underestimating costs?\n"
    "6. Ask them to explain Gradient Descent conceptually \u2014 how does the machine find the "
    "best beta values? Why not just try every combination?\n"
    "7. Give them these specific learned betas and ask them to compute a prediction:\n"
    "   - Intercept (beta_0) = 5000\n"
    "   - Age (beta_1) = 250 per year\n"
    "   - BMI (beta_2) = 300 per unit\n"
    "   - Smoker (beta_3) = 18000 (1=yes, 0=no)\n"
    "   - Dependents (beta_4) = 500 per dependent\n"
    "   New policyholder: age=35, BMI=28, smoker=1, dependents=2\n"
    "8. Ask about Drift \u2014 what real-world changes could make this model wrong over time? "
    "Is it data drift, concept drift, or both?\n\n"
    "IMPORTANT RULES:\n"
    "- Only move to the next step when the student demonstrates understanding of the current step\n"
    "- If they struggle, ask guiding questions but do NOT give them the answer\n"
    "- If they give a correct but shallow answer, push for deeper reasoning (ask WHY)\n"
    "- Keep your responses concise (2-4 sentences) to maintain conversational flow\n"
    "- After covering all 7 steps, wrap up by summarizing their performance"
)

scenario = api_call("POST", "/api/v1/scenarios", {
    "course_id": COURSE_ID,
    "name": "BADM 576 Week 7: ML Process Exercise",
    "description": scenario_desc,
    "persona_id": persona["id"],
    "rubric_id": rubric["id"],
    "is_practice": False,
    "max_turns": 20,
}, token)
print(f"SCENARIO created: {scenario['id']} - {scenario['name']}")

# Step 4: Create Assignment
due = (datetime.utcnow() + timedelta(hours=8)).isoformat()

assignment = api_call("POST", "/api/v1/assignments", {
    "course_id": COURSE_ID,
    "scenario_id": scenario["id"],
    "title": "Week 7: ML Process In-Class Exercise",
    "instructions": (
        "In this exercise, you will apply the 7-step ML process to a new business scenario. "
        "The AI instructor will present you with a case study and guide you through each step: "
        "Task definition, Data, Model, Loss function, Gradient descent, Inference, and Drift. "
        "Answer each question thoughtfully and explain your reasoning. You have one attempt."
    ),
    "max_attempts": 1,
    "due_date": due,
    "is_active": True,
}, token)
print(f"ASSIGNMENT created: {assignment['id']} - {assignment['title']}")

print()
print("=" * 60)
print("ALL DONE! Everything is live.")
print("=" * 60)
print(f"Students go to: http://3.90.88.174:3002")
print(f"Login, click Assignments, and start the exercise")
print(f"Due: {due}")
print()
print("Instructor view: http://3.90.88.174:3002/instructor/assignments")
