# StakeholderSim - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [AI Engineering Concepts](#ai-engineering-concepts)
4. [How It Works](#how-it-works)
5. [Key Components](#key-components)
6. [Enhancement Opportunities](#enhancement-opportunities)
7. [Learning Resources](#learning-resources)

---

## Project Overview

**StakeholderSim** is an AI-powered role-play training platform that helps data science students practice presenting their work to business stakeholders. Students engage in realistic conversations with AI personas (CEOs, CFOs, VPs, etc.) and receive automated feedback based on a professional rubric.

### Core Features
- **6 AI Stakeholder Personas** - Each with unique personalities, concerns, and communication styles
- **Real-time Conversations** - Natural back-and-forth dialogue powered by Claude AI
- **Automated Grading** - AI evaluates conversations against a 6-criteria rubric
- **Instructor Dashboard** - Class analytics, grade review, assignment management
- **Student Dashboard** - Progress tracking, score history, improvement metrics
- **Assignment System** - Due dates, attempt limits, submission tracking

### Tech Stack
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL 15, Redis 7 |
| AI/LLM | Claude API (Anthropic) - claude-sonnet-4-20250514 |
| Infrastructure | Docker, Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  Home   │ │Scenarios│ │  Chat   │ │  Grade  │ │Dashboard│   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                              │                                   │
│                    API Client (TypeScript)                       │
└──────────────────────────────┼───────────────────────────────────┘
                               │ HTTP/REST
┌──────────────────────────────┼───────────────────────────────────┐
│                         Backend (FastAPI)                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      API Routers                         │    │
│  │  /auth  /conversations  /grades  /dashboard  /assignments│    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      Services                            │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │    │
│  │  │ LLM Client   │  │ Conversation │  │   Grading    │   │    │
│  │  │              │  │    Engine    │  │   Engine     │   │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              SQLAlchemy Models (ORM)                     │    │
│  │  User, Course, Persona, Scenario, Conversation,         │    │
│  │  Message, Grade, Assignment, Rubric                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────┼───────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────┴────┐           ┌─────┴─────┐          ┌─────┴─────┐
   │PostgreSQL│           │   Redis   │          │ Claude API │
   │   (DB)   │           │  (Cache)  │          │   (LLM)    │
   └──────────┘           └───────────┘          └───────────┘
```

### Data Flow for a Conversation

```
1. Student selects scenario
        │
        ▼
2. Backend creates Conversation record
        │
        ▼
3. ConversationEngine builds system prompt with persona details
        │
        ▼
4. LLMClient sends request to Claude API
        │
        ▼
5. Stakeholder's opening message returned and stored
        │
        ▼
6. Student sends message → LLMClient → Claude → Response stored
        │
        ▼
7. Loop until conversation ends
        │
        ▼
8. GradingEngine evaluates full transcript
        │
        ▼
9. Grade record created with detailed feedback
```

---

## AI Engineering Concepts

### 1. Prompt Engineering

**What It Is:** Crafting effective instructions for LLMs to produce desired outputs.

**How We Use It:**

#### Persona System Prompts
```python
# backend/app/services/conversation_engine.py

def build_system_prompt(self) -> str:
    return f"""You are {self.persona.name}, {self.persona.title}.

BACKGROUND:
{self.persona.background}

PERSONALITY TRAITS:
{', '.join(self.persona.personality_traits)}

COMMUNICATION STYLE:
{self.persona.communication_style}

KEY CONCERNS:
{chr(10).join(f'- {c}' for c in self.persona.key_concerns)}

CONTEXT FOR THIS MEETING:
{self.context}

INSTRUCTIONS:
- Stay completely in character as {self.persona.name}
- React authentically based on your personality and concerns
- Ask clarifying questions when the student is vague
- Push back on claims that lack evidence
- Show appropriate skepticism based on your role
- Keep responses concise (2-4 sentences typically)
- Never break character or acknowledge being an AI
"""
```

**Key Techniques:**
- **Role Assignment** - "You are [persona name], [title]"
- **Context Injection** - Background, personality, concerns
- **Behavioral Constraints** - "Stay in character", "Keep responses concise"
- **Negative Instructions** - "Never break character"

#### Grading System Prompts
```python
# backend/app/services/grading_engine.py

GRADING_PROMPT = """You are an expert evaluator assessing a student's
stakeholder communication skills.

RUBRIC CRITERIA:
{rubric_criteria}

CONVERSATION TRANSCRIPT:
{transcript}

Evaluate the student's performance on each criterion.
Return a JSON object with this exact structure:
{
  "criteria_scores": {
    "criterion_name": {
      "score": <0-20>,
      "evidence": "specific quote or observation",
      "feedback": "constructive suggestion"
    }
  },
  "overall_feedback": "summary paragraph",
  "strengths": ["strength1", "strength2"],
  "areas_for_improvement": ["area1", "area2"],
  "confidence": <0.0-1.0>
}
"""
```

**Key Techniques:**
- **Structured Output** - Request specific JSON format
- **Evidence-Based Evaluation** - Require quotes/observations
- **Confidence Scoring** - Self-assessment for quality control

---

### 2. Conversation State Management

**What It Is:** Maintaining context across multiple turns in a conversation.

**How We Use It:**

```python
# Loading conversation history for context
def load_history(self, messages: list[Message]):
    for msg in messages:
        role = "user" if msg.role == MessageRole.STUDENT else "assistant"
        self.messages.append({"role": role, "content": msg.content})

# Sending with full context
async def get_response(self, student_message: str) -> str:
    self.messages.append({"role": "user", "content": student_message})

    response = await self.llm_client.generate_response(
        system_prompt=self.system_prompt,
        messages=self.messages,  # Full history included
        temperature=0.7
    )

    self.messages.append({"role": "assistant", "content": response})
    return response
```

**Key Concepts:**
- **Message History** - Store all messages in order
- **Role Mapping** - Map domain roles (student/stakeholder) to LLM roles (user/assistant)
- **Context Window** - Be aware of token limits (~200k for Claude)

---

### 3. LLM API Integration

**What It Is:** Properly integrating with LLM provider APIs.

**How We Use It:**

```python
# backend/app/services/llm_client.py

class LLMClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model  # claude-sonnet-4-20250514

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
            temperature=temperature
        )
        return response.content[0].text
```

**Key Concepts:**
- **System vs User Messages** - System prompt sets behavior, user messages are the conversation
- **Temperature** - 0.0 = deterministic, 1.0 = creative (0.7 is good for conversation)
- **Max Tokens** - Limit response length to control costs and UI
- **Error Handling** - Handle rate limits, timeouts, API errors

---

### 4. Structured Output Parsing

**What It Is:** Getting LLMs to return structured data (JSON) reliably.

**How We Use It:**

```python
async def generate_json_response(
    self,
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 2000
) -> dict:
    response = await self.generate_response(
        system_prompt=system_prompt,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.3  # Lower temp for structured output
    )

    # Extract JSON from response
    try:
        # Handle markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        else:
            json_str = response

        return json.loads(json_str.strip())
    except json.JSONDecodeError:
        # Fallback handling
        return {"error": "Failed to parse response"}
```

**Key Techniques:**
- **Lower Temperature** - More deterministic for structured output
- **Explicit Format Instructions** - Show exact JSON structure expected
- **Robust Parsing** - Handle markdown code blocks, whitespace
- **Fallback Handling** - Graceful degradation on parse failures

---

### 5. AI Confidence Scoring

**What It Is:** Having the AI self-assess its evaluation quality.

**How We Use It:**

```python
# In grading prompt, we ask for confidence score
"confidence": <0.0-1.0>  # How confident in this evaluation

# Then use it for quality control
@router.get("/instructor", response_model=InstructorDashboard)
async def get_instructor_dashboard(...):
    # Flag low-confidence grades for review
    low_confidence_grades = (
        db.query(Grade)
        .filter(Grade.ai_confidence < 0.7)
        .filter(Grade.instructor_override == False)
        .all()
    )
```

**Key Concepts:**
- **Self-Assessment** - LLMs can estimate their own uncertainty
- **Human-in-the-Loop** - Flag uncertain evaluations for human review
- **Override System** - Allow instructors to correct AI grades

---

### 6. Persona Design

**What It Is:** Creating distinct, consistent AI characters.

**How We Use It:**

```python
# backend/app/scripts/seed.py - Persona definitions

personas_data = [
    {
        "name": "Victoria Chen",
        "title": "Chief Executive Officer",
        "background": "Former management consultant with MBA from Wharton...",
        "personality_traits": [
            "Direct and time-conscious",
            "Focuses on strategic impact",
            "Values clear ROI articulation"
        ],
        "communication_style": "Prefers executive summaries...",
        "expertise_areas": ["Strategic planning", "P&L management"],
        "key_concerns": [
            "How does this impact our competitive position?",
            "What's the expected ROI and payback period?"
        ],
        "difficulty_level": "hard"
    },
    # ... 5 more personas with distinct personalities
]
```

**Key Concepts:**
- **Distinct Personalities** - Each persona has unique traits
- **Role-Appropriate Concerns** - CEO cares about strategy, CFO about costs
- **Difficulty Levels** - Some personas are more challenging
- **Consistency** - Detailed backgrounds help maintain character

---

## Key Components

### Backend Services

| Service | File | Purpose |
|---------|------|---------|
| LLM Client | `services/llm_client.py` | Claude API wrapper |
| Conversation Engine | `services/conversation_engine.py` | Manages dialogue flow |
| Grading Engine | `services/grading_engine.py` | Evaluates conversations |

### Database Models

| Model | Purpose |
|-------|---------|
| User | Students, instructors, admins |
| Persona | AI stakeholder characters |
| Scenario | Combines persona + rubric + settings |
| Conversation | A single practice/graded session |
| Message | Individual messages in conversation |
| Grade | Evaluation results with detailed feedback |
| Assignment | Graded scenarios with due dates |
| Rubric | Evaluation criteria and weights |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/conversations/scenarios` | GET | List available scenarios |
| `/api/v1/conversations` | POST | Start new conversation |
| `/api/v1/conversations/{id}/messages` | POST | Send message, get response |
| `/api/v1/conversations/{id}/end` | POST | End conversation |
| `/api/v1/grades/conversations/{id}` | GET | Get grade for conversation |
| `/api/v1/grades/conversations/{id}/grade` | POST | Trigger grading |
| `/api/v1/dashboard/student` | GET | Student stats & progress |
| `/api/v1/dashboard/instructor` | GET | Class analytics |
| `/api/v1/assignments` | CRUD | Assignment management |

---

## Enhancement Opportunities

### 1. Advanced AI Features

#### Multi-Turn Planning
```python
# Current: React to each message independently
# Enhanced: Plan conversation arc

class AdvancedConversationEngine:
    async def plan_conversation(self, student_goals: list[str]):
        """Pre-plan how to guide the conversation."""
        planning_prompt = f"""
        The student wants to practice: {student_goals}
        Plan a conversation arc that will:
        1. Start with an easy opening
        2. Gradually introduce challenges
        3. Test specific skills
        4. End with actionable feedback moment
        """
        self.conversation_plan = await self.llm_client.generate_json_response(...)
```

#### Adaptive Difficulty
```python
# Adjust persona behavior based on student performance
class AdaptivePersona:
    def adjust_difficulty(self, student_score: float):
        if student_score > 80:
            self.challenge_level = "high"
            self.interruption_frequency = "often"
        elif student_score < 50:
            self.challenge_level = "supportive"
            self.hint_frequency = "often"
```

#### Real-Time Coaching
```python
# Provide hints during conversation (practice mode)
async def get_coaching_hint(self, conversation_history: list[Message]) -> str:
    coaching_prompt = """
    Analyze this conversation and provide ONE brief hint
    to help the student improve their next response.
    Focus on: clarity, evidence, or addressing concerns.
    """
    return await self.llm_client.generate_response(...)
```

### 2. Enhanced Grading

#### Rubric Customization
```python
# Allow instructors to create custom rubrics
class CustomRubric:
    criteria: list[Criterion]
    weights: dict[str, float]
    passing_threshold: float

    def to_grading_prompt(self) -> str:
        """Convert custom rubric to grading prompt."""
```

#### Comparative Grading
```python
# Compare against exemplar responses
async def grade_with_exemplars(
    self,
    conversation: Conversation,
    exemplar_conversations: list[Conversation]
) -> Grade:
    """Grade by comparing to high-quality examples."""
```

#### Multi-Evaluator Consensus
```python
# Run multiple evaluations and take consensus
async def grade_with_consensus(self, conversation: Conversation) -> Grade:
    grades = []
    for _ in range(3):
        grade = await self.grade_conversation(conversation)
        grades.append(grade)
    return self.aggregate_grades(grades)
```

### 3. Learning Analytics

#### Skill Progression Tracking
```python
# Track improvement in specific skills over time
class SkillTracker:
    def analyze_progression(self, student_id: UUID) -> SkillReport:
        """
        Returns:
        - Skill-by-skill improvement chart
        - Predicted areas needing work
        - Recommended practice scenarios
        """
```

#### Cohort Comparison
```python
# Compare student to class performance
class CohortAnalytics:
    def get_percentile_rank(self, student_id: UUID, criterion: str) -> float:
        """Where does this student rank in the class for this skill?"""
```

### 4. Content Generation

#### Dynamic Scenario Generation
```python
# Generate new scenarios based on learning objectives
async def generate_scenario(
    self,
    learning_objectives: list[str],
    difficulty: str,
    industry: str
) -> Scenario:
    """Use AI to create new practice scenarios."""
```

#### Personalized Practice Recommendations
```python
# Recommend what to practice next
async def recommend_next_scenario(self, student_id: UUID) -> Scenario:
    """Based on weaknesses, recommend targeted practice."""
```

### 5. Production Readiness

#### Real Authentication
```python
# Replace mock auth with OAuth 2.0
# See docs/PRE_DEPLOYMENT_CHECKLIST.md

from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    ...
)
```

#### Caching & Rate Limiting
```python
# Cache LLM responses for identical inputs
from redis import Redis

class CachedLLMClient:
    def __init__(self):
        self.redis = Redis()
        self.cache_ttl = 3600  # 1 hour

    async def generate_response(self, ...):
        cache_key = self.compute_key(system_prompt, messages)
        cached = self.redis.get(cache_key)
        if cached:
            return cached
        response = await super().generate_response(...)
        self.redis.setex(cache_key, self.cache_ttl, response)
        return response
```

#### Streaming Responses
```python
# Stream LLM responses for better UX
@router.post("/{conversation_id}/messages/stream")
async def send_message_stream(
    conversation_id: UUID,
    request: SendMessageRequest
):
    async def generate():
        async for chunk in engine.get_response_stream(request.content):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 6. Additional Features

| Feature | Description |
|---------|-------------|
| **Voice Mode** | Speech-to-text input, text-to-speech output |
| **Video Personas** | AI-generated video avatars |
| **Peer Review** | Students review each other's conversations |
| **Scenario Builder** | UI for instructors to create scenarios |
| **LMS Integration** | Connect to Canvas, Blackboard, etc. |
| **Mobile App** | React Native or Flutter client |
| **Multi-language** | Support for non-English conversations |
| **Export/Reports** | PDF grade reports, CSV exports |

---

## Learning Resources

### Prompt Engineering
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Learn Prompting](https://learnprompting.org/)

### LLM Application Development
- [LangChain Documentation](https://python.langchain.com/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [Building LLM Apps (Chip Huyen)](https://huyenchip.com/2023/04/11/llm-engineering.html)

### AI Engineering
- [AI Engineering (Swyx)](https://www.latent.space/p/ai-engineer)
- [Patterns for Building LLM-based Systems](https://eugeneyan.com/writing/llm-patterns/)
- [What We Learned from a Year of Building with LLMs](https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/)

### FastAPI & Backend
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)

### Next.js & Frontend
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

## Quick Reference

### Running the Application
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Reset database
docker compose down -v
docker compose up -d db redis
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.scripts.seed
docker compose up -d
```

### Environment Variables
```env
# Required
ANTHROPIC_API_KEY=your-api-key

# Optional
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
DEBUG=true
```

### Test Users
| Key | Role | Access |
|-----|------|--------|
| student1 | Student | Dashboard, assignments, practice |
| student2 | Student | Dashboard, assignments, practice |
| student3 | Student | Dashboard, assignments, practice |
| instructor | Instructor | All above + instructor dashboard |

---

*Built with Claude Code - December 2024*
