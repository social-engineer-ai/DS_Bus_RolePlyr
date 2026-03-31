"""Seed database with test data.

Run with: python -m app.scripts.seed
"""

from uuid import UUID

from passlib.context import CryptContext

from app.database import SessionLocal
from app.models import User, Course, Enrollment, Persona, Rubric, Scenario, Assignment, Quiz, QuizQuestion
from app.models.user import UserRole
from app.models.course import EnrollmentRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Default rubric criteria based on PRD
DEFAULT_RUBRIC_CRITERIA = [
    {
        "name": "business_value_articulation",
        "display_name": "Business Value Articulation",
        "description": "How well the student quantified and communicated business impact",
        "max_points": 25,
        "scoring_guide": {
            "25": "Clearly quantified business impact with specific numbers",
            "20": "Described business value but lacked specific metrics",
            "15": "Mentioned value vaguely without business framing",
            "10": "Focused on technical metrics only",
            "5": "No business value articulation",
        },
    },
    {
        "name": "audience_adaptation",
        "display_name": "Audience Adaptation",
        "description": "How well the student adapted language and approach to the stakeholder",
        "max_points": 20,
        "scoring_guide": {
            "20": "Consistently used accessible language, adapted to stakeholder's concerns",
            "15": "Mostly accessible, occasional jargon without explanation",
            "10": "Frequent jargon, some adaptation to audience",
            "5": "Technical language throughout, no adaptation",
        },
    },
    {
        "name": "handling_objections",
        "display_name": "Handling Objections",
        "description": "How well the student responded to stakeholder concerns and pushback",
        "max_points": 20,
        "scoring_guide": {
            "20": "Addressed all concerns directly, acknowledged limitations honestly",
            "15": "Addressed most concerns, some defensive responses",
            "10": "Struggled with objections, deflected some concerns",
            "5": "Became defensive or dismissive of concerns",
        },
    },
    {
        "name": "clarity_and_structure",
        "display_name": "Clarity and Structure",
        "description": "How clearly and logically the student presented their work",
        "max_points": 15,
        "scoring_guide": {
            "15": "Clear, logical flow; stakeholder could follow easily",
            "10": "Generally clear with some confusing moments",
            "5": "Disorganized, stakeholder had to ask for clarification repeatedly",
        },
    },
    {
        "name": "honesty_and_limitations",
        "display_name": "Honesty and Limitations",
        "description": "How honestly the student discussed model limitations and risks",
        "max_points": 10,
        "scoring_guide": {
            "10": "Proactively mentioned limitations and risks",
            "7": "Acknowledged limitations when asked",
            "3": "Minimized or avoided discussing limitations",
            "0": "Made misleading claims",
        },
    },
    {
        "name": "actionable_recommendation",
        "display_name": "Actionable Recommendation",
        "description": "How clear and specific the student's recommendations were",
        "max_points": 10,
        "scoring_guide": {
            "10": "Clear next steps with specific ask",
            "7": "General recommendation without specifics",
            "3": "No clear recommendation or ask",
        },
    },
]


# Default personas from PRD
DEFAULT_PERSONAS = [
    {
        "name": "Patricia Chen",
        "title": "VP of Talent Acquisition",
        "background": """Patricia has been at the company for 8 years, working her way up from
        recruiter to VP. She's seen AI projects fail before and is skeptical but open-minded
        if shown clear ROI. She cares deeply about candidate experience and the reputation
        of the recruiting team.""",
        "personality": """Skeptical but fair. She asks tough questions but respects those
        who come prepared. She's been burned by overpromising vendors before, so she values
        honesty about limitations.""",
        "concerns": [
            "What's the ROI? How much time/money will this actually save?",
            "What happens when the model is wrong? Who's accountable?",
            "How will this affect candidate experience?",
            "We tried AI screening two years ago and it was a disaster. Why is this different?",
        ],
        "required_questions": [
            "How much time will this save my team per week?",
            "What's the accuracy? What happens when it makes mistakes?",
        ],
    },
    {
        "name": "Marcus Thompson",
        "title": "Director of Recruiting Operations",
        "background": """Marcus has been managing the recruiting operations team for 5 years.
        His team handles resume screening, interview scheduling, and candidate communications.
        He's protective of his team and worried about job security.""",
        "personality": """Protective of his team, detail-oriented, and concerned about
        workload changes. He wants to understand exactly how this will affect day-to-day
        operations and whether his team members will still have jobs.""",
        "concerns": [
            "Will my team lose their jobs?",
            "How much training will this require?",
            "Can we override the AI decisions?",
            "What if the system goes down?",
        ],
        "required_questions": [
            "How will this affect my team's daily workflow?",
            "Can my team override AI decisions when needed?",
        ],
    },
    {
        "name": "Jennifer Walsh",
        "title": "Chief Financial Officer",
        "background": """Jennifer oversees all financial operations and is responsible for
        budget allocation. She's numbers-focused and needs to see clear financial
        justification for any investment.""",
        "personality": """Numbers-focused, direct, and skeptical of projects without clear
        ROI. She appreciates when people come prepared with financial data and realistic
        cost projections.""",
        "concerns": [
            "What's the total cost of implementation?",
            "What's the expected ROI and payback period?",
            "Are there hidden costs (training, maintenance, API fees)?",
            "What if it doesn't work? What's our exit strategy?",
        ],
        "required_questions": [
            "What's the expected cost savings in the first year?",
            "What are the ongoing operational costs?",
        ],
    },
    {
        "name": "David Park",
        "title": "General Counsel",
        "background": """David leads the legal team and is responsible for managing legal
        risk across the organization. He's particularly concerned about AI bias,
        discrimination, and regulatory compliance.""",
        "personality": """Risk-averse, thorough, and focused on worst-case scenarios.
        He appreciates transparency about risks and wants to understand how the organization
        will defend itself if something goes wrong.""",
        "concerns": [
            "Is this model biased against protected classes?",
            "Can we explain why the model made a decision?",
            "What regulations apply to AI in hiring?",
            "How do we respond if someone claims discrimination?",
        ],
        "required_questions": [
            "How have you tested for bias in this model?",
            "Can you explain individual decisions to candidates who ask?",
        ],
    },
    {
        "name": "Sarah Martinez",
        "title": "Engineering Hiring Manager",
        "background": """Sarah manages a team of 15 engineers and is constantly hiring.
        She reviews dozens of candidates per quarter and is frustrated with the current
        process that sends her unqualified candidates.""",
        "personality": """Pragmatic, busy, and results-oriented. She doesn't have time
        for theory - she wants to know if this will actually help her hire better
        engineers faster.""",
        "concerns": [
            "Will I still see the candidates I want to see?",
            "How much of my time will this take?",
            "What if the AI filters out good candidates?",
            "Can I give feedback to improve it?",
        ],
        "required_questions": [
            "How will this change the candidates I see in my pipeline?",
            "How much time will this save me personally?",
        ],
    },
    {
        "name": "Robert Kim",
        "title": "Chief People Officer",
        "background": """Robert oversees all HR functions including recruiting, learning &
        development, and employee experience. He thinks strategically about the employer
        brand and company values.""",
        "personality": """Strategic, values-driven, and focused on the big picture.
        He cares about how AI hiring tools affect the company's reputation and whether
        they align with company values around fairness and inclusion.""",
        "concerns": [
            "Does this align with our diversity and inclusion goals?",
            "How will candidates perceive AI-based screening?",
            "What's our competition doing with AI in hiring?",
            "How does this affect our employer brand?",
        ],
        "required_questions": [
            "How does this support or hinder our diversity goals?",
            "What will candidates think about being screened by AI?",
        ],
    },
]


# Seed users: 2 instructors, 5 students
SEED_USERS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "student1@stakeholdersim.edu",
        "name": "Alex Chen",
        "role": UserRole.STUDENT,
        "password": "student123",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "email": "student2@stakeholdersim.edu",
        "name": "Jordan Rivera",
        "role": UserRole.STUDENT,
        "password": "student123",
    },
    {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "email": "student3@stakeholdersim.edu",
        "name": "Morgan Lee",
        "role": UserRole.STUDENT,
        "password": "student123",
    },
    {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "email": "student4@stakeholdersim.edu",
        "name": "Taylor Kim",
        "role": UserRole.STUDENT,
        "password": "student123",
    },
    {
        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "email": "student5@stakeholdersim.edu",
        "name": "Casey Patel",
        "role": UserRole.STUDENT,
        "password": "student123",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "email": "instructor@stakeholdersim.edu",
        "name": "Dr. Taylor Instructor",
        "role": UserRole.INSTRUCTOR,
        "password": "instructor123",
    },
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "email": "admin@stakeholdersim.edu",
        "name": "Prof. Admin User",
        "role": UserRole.INSTRUCTOR,
        "password": "admin123",
    },
]


def seed_database():
    """Seed the database with test data."""
    print("Seeding database...")

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping.")
            return

        # Create users with hashed passwords
        users = []
        for u in SEED_USERS:
            user = User(
                id=UUID(u["id"]),
                email=u["email"],
                name=u["name"],
                role=u["role"],
                password_hash=pwd_context.hash(u["password"]),
            )
            users.append(user)
        db.add_all(users)
        print(f"  Created {len(users)} users")

        # Create a sample course
        course = Course(
            id=UUID("55555555-5555-5555-5555-555555555555"),
            name="Data Science & Analytics - Fall 2024",
            instructor_id=UUID("33333333-3333-3333-3333-333333333333"),
        )
        db.add(course)
        print("  Created sample course")

        # Enroll all students + instructor
        enrollments = []
        for u in SEED_USERS:
            if u["role"] == UserRole.STUDENT:
                enrollments.append(
                    Enrollment(
                        user_id=UUID(u["id"]),
                        course_id=course.id,
                        role=EnrollmentRole.STUDENT,
                    )
                )
        enrollments.append(
            Enrollment(
                user_id=UUID("33333333-3333-3333-3333-333333333333"),
                course_id=course.id,
                role=EnrollmentRole.INSTRUCTOR,
            )
        )
        db.add_all(enrollments)
        print(f"  Created {len(enrollments)} enrollments")

        # Create default rubric
        rubric = Rubric(
            id=UUID("66666666-6666-6666-6666-666666666666"),
            course_id=course.id,
            name="Stakeholder Communication Rubric",
            criteria=DEFAULT_RUBRIC_CRITERIA,
        )
        db.add(rubric)
        print("  Created default rubric")

        # Create personas
        personas = []
        for i, p_data in enumerate(DEFAULT_PERSONAS, start=1):
            persona = Persona(
                id=UUID(f"7777777{i}-7777-7777-7777-777777777777"),
                course_id=course.id,
                **p_data,
            )
            personas.append(persona)
        db.add_all(personas)
        print(f"  Created {len(personas)} personas")

        # Create scenarios (for first 3 personas)
        scenarios = []
        for i, persona in enumerate(personas[:3], start=1):
            scenario = Scenario(
                id=UUID(f"8888888{i}-8888-8888-8888-888888888888"),
                course_id=course.id,
                name=f"Present to {persona.name}",
                description=f"Practice presenting your data science work to {persona.name}, {persona.title}.",
                persona_id=persona.id,
                rubric_id=rubric.id,
                is_practice=True,
                max_turns=15,
            )
            scenarios.append(scenario)
        db.add_all(scenarios)
        print(f"  Created {len(scenarios)} scenarios")

        # Create 2 graded assignments
        assignments = [
            Assignment(
                id=UUID("99999991-9999-9999-9999-999999999999"),
                course_id=course.id,
                scenario_id=scenarios[0].id,
                title="Assignment 1: Present to VP of Talent Acquisition",
                instructions="Present your resume screening model to Patricia Chen. Explain the business value, address her concerns, and make a clear recommendation.",
                max_attempts=2,
                is_active=True,
            ),
            Assignment(
                id=UUID("99999992-9999-9999-9999-999999999999"),
                course_id=course.id,
                scenario_id=scenarios[2].id,
                title="Assignment 2: Present to CFO",
                instructions="Present your model's financial case to Jennifer Walsh. Focus on ROI, cost analysis, and risk mitigation.",
                max_attempts=2,
                is_active=True,
            ),
        ]
        db.add_all(assignments)
        print(f"  Created {len(assignments)} assignments")

        # Create BADM 558 Big Data Infrastructure Quiz
        badm558_quiz = Quiz(
            id=UUID("aaaa0001-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            course_id=course.id,
            title="BADM 558 — Big Data Infrastructure Quiz Prep",
            description="15 questions covering Kinesis Data Streams + Firehose, Glue ETL, and S3 + Athena. Answer any 5 questions (3 pts each, 15 pts total). Focus on WHY we use each service and KEY DECISIONS when configuring them.",
            max_attempts=10,
            is_active=True,
            show_answers_after_submit=True,
        )
        db.add(badm558_quiz)
        db.flush()

        quiz_questions = [
            # --- KINESIS DATA STREAMS + FIREHOSE (Q1-Q5) ---
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q1. In the ShopStream lab, you sent the same order data to both Kinesis Data Streams and Firehose. The S3 outputs looked very different. Describe the key differences in what each pipeline produced and explain why.",
                correct_answer="Data Streams (via Lambda) produced one JSON file per order with enriched fields (processed_at, priority_flag) organized as processed/year/month/day/. Firehose produced batched NDJSON files of raw untransformed orders organized as year/month/day/hour/. The difference is because Data Streams gives a programmable consumer (Lambda) for custom logic, while Firehose is a managed delivery pipe that buffers and flushes with zero transformation.",
                acceptable_answers=[
                    "lambda", "enriched", "priority_flag", "batched", "NDJSON",
                    "programmable consumer", "zero transformation", "custom processing",
                    "one file per order", "buffered",
                ],
                points=3,
                order_index=0,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text='Q2. A product manager says: "Firehose is simpler and cheaper — why would we ever use Kinesis Data Streams?" Give a specific business scenario where Kinesis Data Streams is necessary and Firehose alone would not work.',
                correct_answer="Firehose cannot run custom logic on individual records. If ShopStream needs to flag high-value orders (over $500) in real time so the fulfillment team can prioritize them immediately, Firehose cannot do this. You need Kinesis Data Streams with a Lambda consumer that inspects each order, applies business logic, enriches the record, and writes the result within sub-second latency.",
                acceptable_answers=[
                    "custom logic", "real-time", "lambda", "enrichment",
                    "fraud detection", "business logic", "sub-second",
                    "individual records", "cannot transform",
                ],
                points=3,
                order_index=1,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q3. In the lab, the Firehose buffer interval was set to 60 seconds. If you increased it to 300 seconds (5 minutes), how would the S3 output change? What is the trade-off?",
                correct_answer="With a 300-second buffer, Firehose would accumulate more records before flushing, producing fewer but larger files. The trade-off is latency vs. efficiency: longer buffers mean data takes longer to appear in S3 (up to 5 minutes delay) but you get fewer larger files that are more efficient for downstream tools like Athena. Shorter buffers give fresher data but create the small file problem.",
                acceptable_answers=[
                    "fewer", "larger files", "latency", "efficiency",
                    "small file problem", "buffer", "delay",
                    "batch", "trade-off",
                ],
                points=3,
                order_index=2,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text='Q4. When you connected Lambda to the Kinesis Data Stream, you configured a "starting position" of "Latest." What does this mean? What would happen if you chose "Trim Horizon" instead?',
                correct_answer='"Latest" means Lambda only processes records that arrive after the trigger is created, ignoring existing data. "Trim Horizon" means Lambda reads from the oldest available record in the stream (Kinesis retains data for 24 hours by default), processing all historical data. Trim Horizon is useful for reprocessing or catching up but can cause a burst of Lambda invocations.',
                acceptable_answers=[
                    "latest", "trim horizon", "oldest", "new events",
                    "historical", "reprocess", "catch up", "backlog",
                    "after the trigger", "24 hours",
                ],
                points=3,
                order_index=3,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q5. In the ShopStream lab, Lambda wrote one S3 object per order. If ShopStream scales to 1 million orders per day, why does this become a problem? Suggest an alternative approach.",
                correct_answer='One million individual S3 objects per day creates the "small file problem." S3 charges per request (PUT, GET, LIST) and query engines like Athena perform poorly with millions of small files. Alternative: batch records in Lambda — accumulate records and write one file per batch (e.g., every 1000 records or 30 seconds). This is essentially what Firehose does automatically.',
                acceptable_answers=[
                    "small file", "batch", "firehose", "per request",
                    "LIST operations", "overhead", "accumulate",
                    "query performance", "cost",
                ],
                points=3,
                order_index=4,
            ),
            # --- GLUE ETL (Q6-Q10) ---
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text='Q6. In the Week 7 lab, the December CSV had a "$" prefix on the price column (e.g., "$29.99"). Could you fix this by simply editing the column type to DOUBLE in the Glue Data Catalog? Why or why not?',
                correct_answer='No. The Data Catalog stores metadata (column names, types, file locations) but does not change the actual data in S3. The string "$29.99" is physically in the CSV. Changing the catalog type to DOUBLE would cause Athena to fail with a parsing error or return NULL. You need ETL to strip the "$" and cast to a number — this is what the Glue Visual Editor SQL transform did with REGEXP_REPLACE. Metadata describes data; ETL transforms data.',
                acceptable_answers=[
                    "metadata", "does not change", "actual data", "ETL",
                    "REGEXP_REPLACE", "parsing error", "NULL",
                    "transform", "strip",
                ],
                points=3,
                order_index=5,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q7. You ran a Glue Crawler on the orders data and it could have created three separate tables (one per month) instead of one unified table. What setting prevents this, and why does it matter?",
                correct_answer='"Create a single schema for each S3 path" under Advanced Options / S3 Schema Grouping when configuring the Crawler. This merges all partitions into one table with a combined schema. Without it, the Crawler creates separate tables for each month, requiring UNION ALL queries instead of simple partitioned queries.',
                acceptable_answers=[
                    "single schema", "schema grouping", "merge",
                    "unified table", "UNION ALL", "partitions",
                    "combined schema", "advanced options",
                ],
                points=3,
                order_index=6,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text='Q8. In the Week 7 lab, November CSV added a "region" column that October didn\'t have, and December renamed "customer_id" to "cust_id." This is called schema evolution. Explain what problems this creates when querying across all three months in Athena.',
                correct_answer="Two problems: (1) The added region column: October rows return NULL for region — manageable, additive schema change. (2) The renamed customer_id to cust_id: CSV maps positionally so data lands correctly, but the Crawler sees two separate columns. October/November have customer_id populated but cust_id NULL; December has cust_id but customer_id NULL. Queries need COALESCE or ETL must standardize the column name.",
                acceptable_answers=[
                    "NULL", "region", "customer_id", "cust_id",
                    "positionally", "COALESCE", "schema evolution",
                    "renamed", "two columns", "additive",
                ],
                points=3,
                order_index=7,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q9. The Glue Visual Editor generated a PySpark script behind the scenes. Why might a data engineer choose to edit that generated script directly instead of continuing to use the visual interface?",
                correct_answer="The Visual Editor has limits. A data engineer would switch to the script for: complex conditional logic, calling external APIs, custom error handling, multi-path pipelines, ML feature engineering, or transformations that can't be expressed in a single SQL block. The generated script is also version-controllable in Git for change tracking, code review, and rollback. Teams often start with the visual editor for prototyping and graduate to scripts.",
                acceptable_answers=[
                    "complex logic", "conditional", "API", "Git",
                    "version control", "error handling", "multi-path",
                    "feature engineering", "limits", "prototyping",
                ],
                points=3,
                order_index=8,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q10. When you configured the Glue ETL job, you set the worker type to G.1X and requested 2 workers. Why does this matter, and what would you change if the dataset was 100x larger?",
                correct_answer="Glue workers are compute resources that cost money per second. G.1X is the smallest worker type (4 vCPUs, 16 GB). For the lab's tiny dataset, 2 workers is enough. For 100x larger, increase workers (e.g., 10-20) so Spark can parallelize across machines, and possibly upgrade to G.2X (8 vCPUs, 32 GB) for more memory. Glue also offers auto-scaling for variable workloads.",
                acceptable_answers=[
                    "workers", "cost", "parallelize", "G.1X", "G.2X",
                    "Spark", "auto-scaling", "compute",
                    "memory", "vCPU",
                ],
                points=3,
                order_index=9,
            ),
            # --- S3 + ATHENA (Q11-Q15) ---
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q11. In the Week 6 lab, you ran the same query on the CSV table and the Parquet table. The query results were identical, but the data scanned was very different. Why does Parquet scan less data, and why does that matter for cost?",
                correct_answer="Parquet is columnar — it stores column values together, so Athena reads only needed columns and skips the rest. CSV is row-based — reading one column requires scanning all columns. Parquet also uses compression (Snappy). This matters because Athena charges $5/TB scanned, so less data scanned = lower cost. At scale, this means thousands of dollars in annual savings.",
                acceptable_answers=[
                    "columnar", "column", "skip", "row-based",
                    "compression", "Snappy", "$5 per TB",
                    "cost", "scan less",
                ],
                points=3,
                order_index=10,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q12. Query 3 in the basic lab (MIN, MAX, AVG on just the price column) showed the biggest gap between CSV and Parquet data scanned. Why did this specific query show the largest difference?",
                correct_answer="Query 3 touched only ONE column (price) out of 10 total. Parquet reads only the price column (~1/10th of data). CSV must scan all 10 columns for every row. Queries 1 and 2 used 2-4 columns, so Parquet still won but the gap was smaller. The fewer columns needed relative to total, the bigger Parquet's advantage — especially powerful for analytics on wide tables.",
                acceptable_answers=[
                    "one column", "price", "10 columns", "1/10",
                    "all columns", "fewer columns", "wider",
                    "advantage", "row by row",
                ],
                points=3,
                order_index=11,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q13. You built a three-tier folder structure: bronze, silver, and gold. Explain what each layer stores and why you would keep the raw CSV in bronze even after converting it to Parquet in silver.",
                correct_answer="Bronze: raw, as-received data in original format — never modified, source of truth. Silver: cleaned, typed, format-converted data (CSV to Parquet) for analytical queries. Gold: pre-computed aggregations and KPIs for dashboards. Keep raw CSV in bronze because: (1) if conversion has a bug, re-run from original; (2) business requirements change, original is always available; (3) auditing and compliance; (4) easier to diagnose schema/quality issues.",
                acceptable_answers=[
                    "bronze", "silver", "gold", "raw", "source of truth",
                    "cleaned", "aggregation", "Parquet",
                    "re-run", "audit", "compliance",
                ],
                points=3,
                order_index=12,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q14. The analytics team runs ad-hoc queries on the 50,000-row book catalog a few times per week. Why is Athena a better fit for this workload than setting up a traditional database like RDS?",
                correct_answer="Athena is serverless — no infrastructure to provision, manage, or pay for when idle. Pay only per query ($5/TB scanned), and with Parquet on 50K rows each query costs fractions of a cent. RDS would require a 24/7 running instance costing money every hour even when idle. For a few queries per week, you'd pay for a server sitting idle 99%+ of the time. Athena queries S3 directly with no loading or ETL needed.",
                acceptable_answers=[
                    "serverless", "idle", "pay per query", "$5/TB",
                    "no infrastructure", "24/7", "running instance",
                    "cost", "S3 directly",
                ],
                points=3,
                order_index=13,
            ),
            QuizQuestion(
                quiz_id=badm558_quiz.id,
                question_type="short_answer",
                question_text="Q15. Your bookstore uploads a new catalog CSV every month. If the new file has a column added in the middle of the existing columns (not at the end), what problem does this cause when Athena queries the CSV table? Why doesn't this problem affect Parquet?",
                correct_answer="CSV maps columns positionally — Athena reads the 1st value as column 1, 2nd as column 2, etc. A column inserted in the middle shifts every subsequent column, mapping wrong data to wrong columns (prices in rating column, etc.) with no error message. Parquet stores column names inside the file and maps by name, not position, so reordering/adding columns doesn't cause misalignment. Parquet is inherently safer for schema evolution.",
                acceptable_answers=[
                    "positionally", "position", "shift", "wrong column",
                    "by name", "column name", "schema evolution",
                    "no error", "misalignment", "embedded",
                ],
                points=3,
                order_index=14,
            ),
        ]
        db.add_all(quiz_questions)
        print(f"  Created BADM 558 quiz with {len(quiz_questions)} questions")

        db.commit()

        # Print credentials table
        print("\n" + "=" * 70)
        print("SEED CREDENTIALS")
        print("=" * 70)
        print(f"{'Role':<14} {'Email':<36} {'Password'}")
        print("-" * 70)
        for u in SEED_USERS:
            print(f"{u['role'].value:<14} {u['email']:<36} {u['password']}")
        print("=" * 70)
        print("\nDatabase seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
