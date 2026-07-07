# PRD Development Prompt — Conversational AI Assessment Platform

You are helping me design and write a PRD for a conversational AI assessment platform. I need you to be my product thinking partner — push back on ideas, ask clarifying questions, and help me think through edge cases. I especially need your help thinking about the pedagogical and assessment design — how to structure conversations that genuinely probe understanding vs. surface-level recall.

## Product Vision

The platform uses AI-powered conversational assessment to test whether someone truly understands what they claim to know. It's NOT a simulation — it's an intelligent interviewer.

### The Problem

Students increasingly use AI to complete assignments. Traditional assessments can't distinguish between:
- **Deep understanding:** "I used AI to help implement, but I drove the thinking, made the decisions, and understand why everything works the way it does"
- **Surface-level completion:** "I gave AI the prompt, it gave me the answer, I submitted it — I can describe what it does but I don't really understand the tradeoffs, alternatives, or reasoning behind it"

Only a skilled interviewer asking probing, adaptive follow-up questions can reliably tell the difference. This platform IS that interviewer.

### Three Use Cases

1. **Submission Verification (Instructor-assigned):** Instructor assigns a conversational interview after students submit work. The AI interviews them about their submission — probing their reasoning, decision-making process, understanding of alternatives, and ability to think on their feet. This isn't about catching cheaters — it's about assessing the DEPTH of understanding behind submitted work.

2. **Conceptual Assessment (Instructor-assigned):** Instructor creates a conversational assessment on any topic taught in the course. The AI tests conceptual understanding through dialogue — not "what is X?" but "why would you choose X over Y in this situation?" and "what would happen if we changed this constraint?"

3. **Self-Assessment (Open/voluntary):** Anyone can use the platform to genuinely test their own command over something. You built a project with AI help? Come here and find out which aspects you truly understand and which you're shaky on. Practice, get feedback, reinforce. This is a learning tool, not just an evaluation tool.

### Key Design Challenge I Need Your Help With

I want to design the conversation system to assess ASPECTS of understanding — not just "do you know topic X" but the different dimensions of knowing something:
- Can they explain WHY, not just WHAT?
- Can they reason about alternatives and tradeoffs?
- Can they predict what would happen if conditions changed?
- Can they connect this concept to related concepts?
- Can they identify limitations and edge cases?
- Do they understand the decisions they made, or just the output?
- Can they teach it back / explain it to a non-expert?
- Can they apply the concept in a novel context?

I want the AI to adaptively probe these aspects and produce an assessment that maps the SHAPE of someone's understanding — showing which aspects they command and which they have gaps in. Not a single score, but a multi-dimensional picture.

### Important Nuance

Yes, a very smart person could fool the interviewer by studying deeply after using AI. But that's actually fine — if they studied deeply enough to fool a strong interviewer, they've genuinely learned the material. The system creates an incentive to actually understand, whether that happens before or after initial completion.

---

## Current Product (what's already built)

### Tech Stack
- **Backend:** FastAPI + PostgreSQL 15 + SQLAlchemy 2.0 + Alembic + Pydantic v2
- **Frontend:** Next.js 14 (App Router) + React 18 + TypeScript + Tailwind CSS
- **AI:** Anthropic Claude (claude-sonnet-4-20250514) via `anthropic` Python SDK
- **Auth:** JWT (python-jose) + bcrypt (passlib), 24h token expiry
- **Infra:** Docker Compose (dev + prod), PostgreSQL 15, Redis 7, EC2 deployment
- **File Processing:** PyPDF2 + python-docx (already integrated for rubric material upload)

### Current Database Models (exact fields)

**User:** id (UUID), email, name, role (STUDENT|INSTRUCTOR|ADMIN), password_hash, created_at

**Course:** id, name, instructor_id (FK→users), created_at

**Enrollment:** id, user_id, course_id, role (STUDENT|TA|INSTRUCTOR), UNIQUE(user_id, course_id)

**Persona:** id, course_id, name, title, background (text), personality (text), concerns (JSONB array of strings), required_questions (JSONB array of strings), is_active, created_at
- Example: "Patricia Chen, VP of Talent Acquisition" with personality="skeptical, ROI-focused", concerns=["budget impact", "implementation timeline"], required_questions=["What's the expected ROI?"]

**Rubric:** id, course_id, name, criteria (JSONB array of criterion objects), created_at
- Each criterion: {name (snake_case), display_name, description, max_points, scoring_guide: {score→description}}
- Example: "business_value_articulation" with 25 max_points and scoring guide from 0-25

**Scenario:** id, course_id, name, description (text — can be rich scenario instructions), persona_id (FK), rubric_id (FK), is_practice (bool), max_turns (int, default 15), created_at
- Links a persona + rubric together into a playable scenario

**Assignment:** id, course_id, scenario_id (FK), title, instructions (text), due_date, max_attempts (default 1), is_active, created_at
- Makes a scenario into a graded assignment with due dates and attempt limits

**Conversation:** id, user_id, scenario_id, assignment_id (nullable), context (text — student's project description), mode (PRACTICE|GRADED), status (IN_PROGRESS|COMPLETED|ABANDONED), started_at, completed_at, turn_count, violation_count, violation_log (JSONB), ended_at, total_active_seconds

**Message:** id, conversation_id, role (STUDENT|STAKEHOLDER), content (text), created_at

**Grade:** id, conversation_id (unique), rubric_id, criteria_scores (JSONB — {criterion_name: {score, max_score, evidence, feedback}}), total_score (decimal), overall_feedback, strengths (JSONB array), areas_for_improvement (JSONB array), ai_confidence (0-1), graded_by (AI|INSTRUCTOR), instructor_override, override_reason, graded_at

**DailyAnalytics:** id, course_id, date, total_conversations, total_practice, total_graded, avg_score, common_struggles (JSONB)

### Current AI Services

**ConversationEngine** (backend/app/services/conversation_engine.py):
- Takes a Persona + student context + optional scenario_description
- `build_system_prompt()`: If scenario description > 200 chars, uses it as the core prompt (custom scenario mode). Otherwise uses default stakeholder presentation mode
- Includes persona background, personality, concerns, required questions in system prompt
- Behavior rules baked into prompt: stay in character, push back on vague answers, probe deep, don't help the student
- `get_opening_message()`, `get_response()`, `get_closing_message()` — all call Claude
- Temperature: 0.8 opening, 0.7 response
- Max tokens: 300 opening, 400 response, 200 closing
- Maintains conversation history for context

**GradingEngine** (backend/app/services/grading_engine.py):
- Takes a Rubric + Conversation transcript + Persona context
- Builds detailed grading prompt with rubric criteria and scoring guides
- Calls Claude with temperature=0.3 (JSON mode)
- Returns: criteria_scores, total_score, overall_feedback, strengths, areas_for_improvement, confidence (0-1)
- Confidence < 0.7 flags for instructor review

**LLMClient** (backend/app/services/llm_client.py):
- Wraps Anthropic Python SDK, singleton pattern
- `generate_response()` and `generate_json_response()` methods
- Model: claude-sonnet-4-20250514

### Current Instructor Tools (already built)
1. **CRUD UI** for Personas, Rubrics, Scenarios, Assignments — form-based pages at `/instructor/*`
2. **AI Rubric Builder** — chat interface at `/instructor/rubrics/create`:
   - Upload PDF/DOCX course materials (text extracted via PyPDF2/python-docx)
   - Chat with Claude to iteratively build a rubric
   - Preview draft in side panel, save when ready
   - Backend: `POST /api/v1/rubrics/upload-material` (file upload) + `POST /api/v1/rubrics/chat` (chat with materials context)

### Current Student Flow
1. Login → dashboard with stats, progress chart, recent activity
2. Browse practice scenarios → select one → describe their project (10-2000 chars) → start conversation
3. Chat with AI persona (turn-based, max turns configurable) → persona stays in character, pushes back, asks tough questions
4. End conversation → get AI grade with per-criterion scores, evidence, feedback
5. Graded assignments: limited attempts, due dates, violation tracking (screen lock with 4-strike escalation), active time tracking

### Current Naming That Needs Rethinking
- The current system calls the AI role "STAKEHOLDER" in messages — built around stakeholder presentation scenarios
- Persona model was designed for stakeholder characters (VP, CFO, etc.)
- The conversation engine's default mode is "stakeholder presentation"
- These need to be generalized for the new interviewer/assessor framing

### Seed Data (current, will need new examples)
- 6 personas (all business executives: VP Talent, Dir Recruiting, CFO, General Counsel, Engineering Manager, Chief People Officer)
- 1 rubric: "Stakeholder Communication Rubric" (business value, audience adaptation, handling objections, clarity, honesty, recommendations)
- 3 practice scenarios, 2 graded assignments
- 5 students, 2 instructors

### Existing API Endpoints (complete list)
- **Auth:** POST /signup, POST /login, GET /me
- **Conversations:** GET /scenarios, POST / (start), GET /{id}, POST /{id}/messages, POST /{id}/end, POST /{id}/violations, GET / (list)
- **Grades:** GET /conversations/{id}, POST /conversations/{id}/grade, POST /conversations/{id}/override, GET /needs-review
- **Dashboard:** GET /student, GET /instructor
- **Personas:** POST /, GET /, GET /{id}, PUT /{id}, DELETE /{id}
- **Rubrics:** POST /, GET /, GET /{id}, PUT /{id}, DELETE /{id}, POST /upload-material, POST /chat
- **Scenarios:** POST /, GET /, GET /{id}, PUT /{id}, DELETE /{id}
- **Assignments:** POST /, GET /, GET /student, GET /{id}, PUT /{id}, DELETE /{id}, GET /{id}/submissions

### Deployment & Config
- Docker Compose with 4 services: PostgreSQL 15, Redis 7, FastAPI backend, Next.js frontend
- Single Alembic migration (001_initial_schema.py) covers all tables
- Seed script creates all sample data
- Startup: alembic upgrade head → seed.py → uvicorn
- Production: docker-compose.prod.yml overlay, 4 uvicorn workers, EC2 deployment
- Frontend port 3002 (dev), backend port 8000

---

## FEATURE 1: Conversational Assignment Builder

I want an AI-powered "Assignment Builder" where instructors create everything through conversation — no forms. The instructor chats with an AI assistant that helps them define the assessment, test it, and deploy it.

### What the instructor should be able to do:

1. **Upload content** — syllabi, case studies, PDFs, lecture notes, assignment prompts, student submission examples, learning objectives (PDF/DOCX extraction already works)

2. **Conversationally define everything:**
   - **Assessment context:** What topic/submission is being assessed, what the student should have learned/done
   - **Interviewer persona:** How the AI interviewer should behave — Socratic? Direct? Supportive? Challenging? What expertise level should it project?
   - **Interaction guidelines:** How the interviewer should conduct the conversation — start broad then narrow? Go deep on first weakness found? Cover all aspects evenly? How much rope to give before challenging?
   - **Guardrails:** What the interviewer should NOT do (don't teach, don't give answers, don't be adversarial to the point of shutting students down), what topics are in/out of scope, when to move on vs. dig deeper
   - **Assessment rubric:** What aspects of understanding to probe, what "deep understanding" vs "surface understanding" vs "no understanding" looks like for each aspect, point allocations
   - **Assignment metadata:** Title, instructions, time limits, attempts, due date

3. **Test the assessment** — instructor plays as student, has a test conversation with the configured interviewer, then refines

4. **Iterate** — "make it probe more on tradeoffs" / "it's too aggressive, tone it down" / "add a criterion for whether they can connect this to [related topic]"

5. **Deploy** — publish for students

### Key Design Questions:
- How do we formally represent "interaction guidelines" and "guardrails" so the conversation engine enforces them? Currently persona has `concerns` and `required_questions` but nothing for behavioral rules
- Should guidelines/guardrails be separate models or embedded in Scenario/Persona?
- How does the builder AI differ architecturally from the interviewer AI?
- How do we handle the "test mode" → "edit mode" transitions smoothly?

---

## FEATURE 2: Quiz System

I want to add traditional quiz/assessment alongside conversational assessment. Instructors upload a Word or JSON document in a specific format.

### Capabilities:
1. **Upload Word/JSON document** with quiz questions in a defined format
2. **Question types:** Multiple choice, multiple select, True/False, short answer (AI-graded), essay (AI-graded)
3. **Quiz settings:** Time limit, attempts, randomize questions/answers, show/hide correct answers, passing score
4. **Student quiz UI:** Timer, progress, question navigation, flag for review
5. **Auto-grading** for objective questions + **AI grading** for subjective (using existing Claude integration)
6. **Analytics:** Question-level stats, common wrong answers, average scores, time per question

### Proposed Quiz Document Format:
```json
{
  "title": "Midterm Quiz - Data Science Concepts",
  "instructions": "Answer all questions. You have 60 minutes.",
  "questions": [
    {
      "type": "multiple_choice",
      "text": "Which metric is most appropriate for imbalanced classification?",
      "options": ["Accuracy", "F1-Score", "R-Squared", "MSE"],
      "correct": "F1-Score",
      "points": 5,
      "explanation": "F1-Score balances precision and recall..."
    },
    {
      "type": "multiple_select",
      "text": "Which of the following are unsupervised learning methods? (Select all)",
      "options": ["K-Means", "Linear Regression", "PCA", "Random Forest", "DBSCAN"],
      "correct": ["K-Means", "PCA", "DBSCAN"],
      "points": 5,
      "partial_credit": true,
      "explanation": "K-Means and DBSCAN are clustering; PCA is dimensionality reduction..."
    },
    {
      "type": "true_false",
      "text": "Regularization increases model complexity.",
      "correct": false,
      "points": 2,
      "explanation": "Regularization penalizes complexity to prevent overfitting."
    },
    {
      "type": "short_answer",
      "text": "Explain the bias-variance tradeoff in 2-3 sentences.",
      "rubric": "Should mention: model complexity, underfitting, overfitting, generalization",
      "points": 10,
      "max_words": 150
    },
    {
      "type": "essay",
      "text": "Compare and contrast batch gradient descent and stochastic gradient descent. When would you choose one over the other?",
      "rubric": "Should cover: convergence speed, memory usage, noise in updates, local minima, dataset size considerations",
      "points": 20,
      "max_words": 500
    }
  ]
}
```

For Word documents, please propose a heading/formatting convention that can be reliably parsed.

---

## FEATURE 3 (Critical — need your deep thinking): Conversational Assessment Design

This is the core intellectual challenge. I need you to help me think through HOW the AI interviewer should conduct assessments. This isn't just prompt engineering — it's assessment methodology.

### Questions I need help answering:

**Assessment Dimensions / Aspects:**
- What are the right "aspects" or "dimensions" of understanding to assess? I listed some above (explain why, reason about alternatives, predict changes, connect concepts, identify limitations, etc.) — are these the right ones? What's missing? How do they relate to established learning taxonomies (Bloom's, SOLO, etc.)?
- Should the aspects be fixed (platform-level) or configurable per assessment?
- How many aspects can a single conversation realistically probe in 10-20 turns?

**Conversation Strategy:**
- How should the interviewer decide what to ask next? Breadth-first (touch all aspects) vs. depth-first (go deep on first weakness)?
- How should it adapt based on student responses? If a student gives a great answer, does it move on or probe deeper? If they stumble, does it give them a chance to recover or move to the next aspect?
- How does it distinguish between "doesn't know" vs "knows but can't articulate well" vs "partially knows"?
- Should there be a conversation plan/structure that the AI follows, or should it be fully adaptive?

**The "Shape of Understanding" Output:**
- I want the assessment output to show a multi-dimensional picture, not just a score. Think radar charts, aspect-by-aspect breakdowns showing where the student is strong vs. weak
- How should this differ from the current rubric-based grading (which produces per-criterion scores)?
- Can we produce something that's genuinely useful for learning — showing the student exactly which aspects to work on?

**Anti-Gaming:**
- How do we make it hard to game? If someone memorizes definitions, the interviewer should detect that they can recite but can't apply
- What conversational techniques make it hard to fake understanding? (Novel scenarios, "what if" variations, asking them to predict, asking them to critique a wrong approach, etc.)
- How do we balance rigor with not being so adversarial that it causes anxiety?

**Self-Assessment Mode:**
- When someone is using this voluntarily to test themselves, how should the experience differ? More supportive? More explanatory? Should it teach after assessing?
- Should it provide immediate aspect-by-aspect feedback after each exchange, or only at the end?

---

## What I Need From You

Help me develop a comprehensive PRD covering BOTH the technical product and the assessment methodology:

1. **Assessment Framework** — the pedagogical model for how conversational assessment works, what aspects to probe, how to structure conversations, how to score. Ground this in learning science (Bloom's taxonomy, SOLO taxonomy, Socratic method, etc.)
2. **User Journeys** — step-by-step flows for instructors (creating assessments via chat) and students (taking them — both assigned and self-directed)
3. **Information Architecture** — new data models needed, relationship to existing models, database migrations needed
4. **AI System Design** — the interviewer engine, the builder engine, the grading/analysis engine, prompt architecture for each
5. **Interaction Design** — UI for builder (extend the existing two-panel chat+preview pattern), interview, results/feedback, quiz-taking
6. **Guardrail & Guideline System** — formal representation of interaction rules, how the conversation engine enforces them during interviews
7. **Quiz Engine** — document parsing (Word + JSON), question types, auto-grading, AI grading for subjective questions, analytics
8. **Understanding Map** — how to represent, compute, and display the multi-dimensional understanding assessment (the "shape of understanding")
9. **Technical Architecture** — new API endpoints, database schema changes, new services, integration with existing codebase
10. **Self-Assessment Mode** — how it differs from graded mode, the learning loop design, feedback approach
11. **Edge Cases & Risks** — gaming strategies, student anxiety, AI limitations/hallucination, partial completion, what happens when AI is wrong
12. **MVP Scope & Phasing** — smallest useful version of each feature, what to build first, what waits for v2, what waits for v3

## My Constraints
- Solo developer — pragmatic shortcuts welcome, don't over-engineer
- Students: business undergrads, not technical users
- Instructors: business faculty, not technical — the chat-based builder exists to lower the barrier to creating assessments
- Current database has a single Alembic migration — need careful migration planning
- Using Anthropic Claude API for all AI features
- The existing AI Rubric Builder chat UI (two-panel: chat on left + preview on right) is a proven pattern to extend
- Already have PDF/DOCX text extraction working

## How I Want to Work Together
- Start by asking me clarifying questions
- Then let's deeply discuss the **assessment methodology FIRST** — the conversation design and "aspects of understanding" framework — before jumping to technical architecture. This is the hard part and will inform everything else
- Then propose overall architecture
- Then work through each PRD section iteratively
- Challenge my assumptions aggressively — if something is over-engineered for a solo dev, say so
- Consider how quiz and conversation features can share infrastructure (grading, analytics, assignments, the assignment model)
- Output a final PRD document I can bring to Claude Code for implementation

Let's start. What questions do you have for me?
