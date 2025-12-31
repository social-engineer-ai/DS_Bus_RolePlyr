"""Seed database with test data.

Run with: python -m app.scripts.seed
"""

from uuid import UUID

from app.database import SessionLocal, engine, Base
from app.models import User, Course, Enrollment, Persona, Rubric, Scenario
from app.models.user import UserRole
from app.models.course import EnrollmentRole


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


def seed_database():
    """Seed the database with test data."""
    print("Seeding database...")

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping.")
            return

        # Create users (matching mock auth users)
        users = [
            User(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                email="student@example.com",
                name="Alex Student",
                role=UserRole.STUDENT,
            ),
            User(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                email="student2@example.com",
                name="Jordan Student",
                role=UserRole.STUDENT,
            ),
            User(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                email="instructor@example.com",
                name="Dr. Taylor Instructor",
                role=UserRole.INSTRUCTOR,
            ),
            User(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                email="admin@example.com",
                name="System Admin",
                role=UserRole.ADMIN,
            ),
        ]
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

        # Enroll users
        enrollments = [
            Enrollment(
                user_id=UUID("11111111-1111-1111-1111-111111111111"),
                course_id=course.id,
                role=EnrollmentRole.STUDENT,
            ),
            Enrollment(
                user_id=UUID("22222222-2222-2222-2222-222222222222"),
                course_id=course.id,
                role=EnrollmentRole.STUDENT,
            ),
            Enrollment(
                user_id=UUID("33333333-3333-3333-3333-333333333333"),
                course_id=course.id,
                role=EnrollmentRole.INSTRUCTOR,
            ),
        ]
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

        # Create sample scenarios
        scenarios = []
        for i, persona in enumerate(personas[:3], start=1):  # Create scenarios for first 3 personas
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

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
