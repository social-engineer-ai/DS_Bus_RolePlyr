# AI Engineering in StakeholderSim

## Executive Summary

StakeholderSim is an AI-powered training platform that demonstrates production-grade AI engineering patterns. This document details the AI components, architecture decisions, and engineering techniques used to build a reliable, scalable LLM-based application.

---

## Table of Contents

1. [Features Built](#features-built)
2. [AI Engineering Architecture](#ai-engineering-architecture)
3. [Core AI Components](#core-ai-components)
4. [Prompt Engineering Deep Dive](#prompt-engineering-deep-dive)
5. [AI Design Patterns Used](#ai-design-patterns-used)
6. [Data Flow & State Management](#data-flow--state-management)
7. [Quality Assurance & Reliability](#quality-assurance--reliability)
8. [Key Learnings](#key-learnings)

---

## Features Built

### 1. AI-Powered Conversation System
| Feature | Description | AI Technique |
|---------|-------------|--------------|
| Stakeholder Personas | 6 distinct AI characters with unique personalities | Role-based prompting, personality injection |
| Context-Aware Responses | Maintains conversation context across turns | Message history management |
| Dynamic Difficulty | Personas challenge students based on their role | Behavioral constraints in prompts |
| Natural Endings | AI detects when to conclude conversations | Turn-based logic + sentiment analysis |

### 2. Automated Grading System
| Feature | Description | AI Technique |
|---------|-------------|--------------|
| Rubric Evaluation | Scores against 6 criteria (100 points total) | Structured output generation |
| Evidence Extraction | Cites specific quotes from conversation | In-context retrieval |
| Feedback Generation | Personalized improvement suggestions | Conditional generation |
| Confidence Scoring | AI self-assesses evaluation quality | Calibrated uncertainty |

### 3. Intelligent Analytics
| Feature | Description | AI Technique |
|---------|-------------|--------------|
| Common Struggles Detection | Identifies class-wide weak areas | Pattern aggregation |
| Low-Confidence Flagging | Routes uncertain grades for review | Threshold-based routing |
| Progress Tracking | Measures improvement over time | Score trend analysis |

---

## AI Engineering Architecture

### High-Level AI System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            STAKEHOLDER SIM                                   │
│                         AI Engineering Layer                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                      APPLICATION LAYER                              │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │     │
│  │  │   Chat UI   │  │  Grade UI   │  │ Dashboard   │                 │     │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │     │
│  └─────────┼────────────────┼────────────────┼────────────────────────┘     │
│            │                │                │                               │
│  ┌─────────┼────────────────┼────────────────┼────────────────────────┐     │
│  │         ▼                ▼                ▼      API LAYER          │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │     │
│  │  │Conversation │  │   Grading   │  │  Analytics  │                 │     │
│  │  │  Endpoints  │  │  Endpoints  │  │  Endpoints  │                 │     │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │     │
│  └─────────┼────────────────┼────────────────┼────────────────────────┘     │
│            │                │                │                               │
│  ┌─────────┼────────────────┼────────────────┼────────────────────────┐     │
│  │         ▼                ▼                ▼     AI SERVICE LAYER    │     │
│  │  ╔═════════════╗  ╔═════════════╗  ╔═════════════╗                 │     │
│  │  ║ CONVERSATION║  ║   GRADING   ║  ║  ANALYTICS  ║                 │     │
│  │  ║   ENGINE    ║  ║   ENGINE    ║  ║   ENGINE    ║                 │     │
│  │  ╚══════╤══════╝  ╚══════╤══════╝  ╚══════╤══════╝                 │     │
│  │         │                │                │                         │     │
│  │         └────────────────┼────────────────┘                         │     │
│  │                          ▼                                          │     │
│  │                   ╔═════════════╗                                   │     │
│  │                   ║  LLM CLIENT ║                                   │     │
│  │                   ║  (Wrapper)  ║                                   │     │
│  │                   ╚══════╤══════╝                                   │     │
│  └──────────────────────────┼──────────────────────────────────────────┘     │
│                             │                                                │
├─────────────────────────────┼────────────────────────────────────────────────┤
│                             ▼           EXTERNAL SERVICES                    │
│                   ┌─────────────────┐                                        │
│                   │   Claude API    │                                        │
│                   │   (Anthropic)   │                                        │
│                   │                 │                                        │
│                   │ claude-sonnet-4-│                                        │
│                   │   20250514      │                                        │
│                   └─────────────────┘                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

### AI Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONVERSATION FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Student                    System                         Claude API       │
│      │                         │                                │            │
│      │  1. Select Scenario     │                                │            │
│      │────────────────────────>│                                │            │
│      │                         │                                │            │
│      │                         │  2. Load Persona + Build       │            │
│      │                         │     System Prompt              │            │
│      │                         │  ┌──────────────────────┐      │            │
│      │                         │  │ "You are Victoria    │      │            │
│      │                         │  │  Chen, CEO..."       │      │            │
│      │                         │  └──────────────────────┘      │            │
│      │                         │                                │            │
│      │                         │  3. Request Opening Message    │            │
│      │                         │───────────────────────────────>│            │
│      │                         │                                │            │
│      │                         │<───────────────────────────────│            │
│      │                         │  4. "Good morning. I have      │            │
│      │  5. Display Opening     │      15 minutes. What do       │            │
│      │<────────────────────────│      you have for me?"         │            │
│      │                         │                                │            │
│      │  6. Student Types       │                                │            │
│      │     Message             │                                │            │
│      │────────────────────────>│                                │            │
│      │                         │                                │            │
│      │                         │  7. Append to History +        │            │
│      │                         │     Request Response           │            │
│      │                         │  ┌──────────────────────┐      │            │
│      │                         │  │ messages: [          │      │            │
│      │                         │  │   {assistant: "..."},│      │            │
│      │                         │  │   {user: "..."}      │──────>            │
│      │                         │  │ ]                    │      │            │
│      │                         │  └──────────────────────┘      │            │
│      │                         │                                │            │
│      │                         │<───────────────────────────────│            │
│      │  8. Display Response    │  9. Stakeholder Response       │            │
│      │<────────────────────────│                                │            │
│      │                         │                                │            │
│      │        ... continue until conversation ends ...          │            │
│      │                         │                                │            │
│      │  N. End Conversation    │                                │            │
│      │────────────────────────>│                                │            │
│      │                         │                                │            │
│      │                         │  N+1. Trigger Grading          │            │
│      │                         │───────────────────────────────>│            │
│      │                         │                                │            │
│      │                         │<───────────────────────────────│            │
│      │  N+2. Show Grade        │  N+2. Structured Grade JSON    │            │
│      │<────────────────────────│                                │            │
│      │                         │                                │            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core AI Components

### Component 1: LLM Client (`llm_client.py`)

**Purpose:** Abstraction layer for Claude API communication

```
┌─────────────────────────────────────────────────────────────┐
│                       LLM CLIENT                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  generate_      │    │  generate_json_ │                 │
│  │  response()     │    │  response()     │                 │
│  │                 │    │                 │                 │
│  │ • Text output   │    │ • JSON output   │                 │
│  │ • Conversation  │    │ • Grading       │                 │
│  │ • temp=0.7      │    │ • temp=0.3      │                 │
│  └────────┬────────┘    └────────┬────────┘                 │
│           │                      │                          │
│           └──────────┬───────────┘                          │
│                      ▼                                      │
│           ┌─────────────────┐                               │
│           │  Claude API     │                               │
│           │  messages.create│                               │
│           └─────────────────┘                               │
│                                                              │
│  Key Parameters:                                             │
│  ├── model: claude-sonnet-4-20250514                        │
│  ├── max_tokens: 500 (conversation) / 2000 (grading)        │
│  ├── temperature: 0.7 (creative) / 0.3 (structured)         │
│  └── system: persona prompt / grading prompt                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Code Implementation:**
```python
class LLMClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 500,
        temperature: float = 0.7  # Higher for natural conversation
    ) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
            temperature=temperature
        )
        return response.content[0].text

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
            temperature=0.3  # Lower for structured output
        )
        return self._parse_json(response)
```

---

### Component 2: Conversation Engine (`conversation_engine.py`)

**Purpose:** Manages persona behavior and conversation state

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONVERSATION ENGINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        PERSONA INJECTION                             │    │
│  │                                                                      │    │
│  │   Persona Object                    System Prompt Output             │    │
│  │   ┌────────────────┐                ┌────────────────────────────┐  │    │
│  │   │ name: "Victoria│                │ You are Victoria Chen, CEO │  │    │
│  │   │   Chen"        │                │                            │  │    │
│  │   │ title: "CEO"   │ ──────────────>│ BACKGROUND:                │  │    │
│  │   │ background:... │   build_       │ Former McKinsey partner... │  │    │
│  │   │ traits: [...]  │   system_      │                            │  │    │
│  │   │ concerns: [...] │   prompt()    │ PERSONALITY:               │  │    │
│  │   └────────────────┘                │ Direct, time-conscious...  │  │    │
│  │                                     │                            │  │    │
│  │                                     │ KEY CONCERNS:              │  │    │
│  │                                     │ - ROI and payback period   │  │    │
│  │                                     │ - Competitive advantage    │  │    │
│  │                                     │                            │  │    │
│  │                                     │ INSTRUCTIONS:              │  │    │
│  │                                     │ - Stay in character        │  │    │
│  │                                     │ - Push back on vague claims│  │    │
│  │                                     │ - Never break character    │  │    │
│  │                                     └────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     CONVERSATION STATE                               │    │
│  │                                                                      │    │
│  │   messages: list[dict]                                               │    │
│  │   ┌──────────────────────────────────────────────────────────────┐  │    │
│  │   │ [                                                             │  │    │
│  │   │   {"role": "assistant", "content": "Good morning..."},       │  │    │
│  │   │   {"role": "user", "content": "I'd like to present..."},     │  │    │
│  │   │   {"role": "assistant", "content": "Interesting. What's..."},│  │    │
│  │   │   {"role": "user", "content": "We expect 15% increase..."},  │  │    │
│  │   │   ...                                                         │  │    │
│  │   │ ]                                                             │  │    │
│  │   └──────────────────────────────────────────────────────────────┘  │    │
│  │                                                                      │    │
│  │   Each API call includes FULL history for context continuity        │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        KEY METHODS                                   │    │
│  │                                                                      │    │
│  │   get_opening_message()  → First stakeholder message                │    │
│  │   get_response(msg)      → Response to student message              │    │
│  │   get_closing_message()  → Wrap-up when conversation ends           │    │
│  │   should_end_conversation() → Check turn limits                     │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Component 3: Grading Engine (`grading_engine.py`)

**Purpose:** Evaluates conversations against rubric using structured output

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GRADING ENGINE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT                           PROCESSING                    OUTPUT        │
│  ┌──────────────┐               ┌──────────────┐              ┌──────────┐  │
│  │ Conversation │               │              │              │  Grade   │  │
│  │ Transcript   │──────────────>│   Claude     │─────────────>│  Object  │  │
│  │              │               │   API        │              │          │  │
│  │ + Rubric     │               │              │              │ • scores │  │
│  │ + Persona    │               │              │              │ • feedback│  │
│  └──────────────┘               └──────────────┘              │ • conf.  │  │
│                                                                └──────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    GRADING PROMPT STRUCTURE                          │    │
│  │                                                                      │    │
│  │  ┌────────────────────────────────────────────────────────────────┐ │    │
│  │  │ SYSTEM PROMPT                                                   │ │    │
│  │  │                                                                 │ │    │
│  │  │ You are an expert evaluator assessing stakeholder              │ │    │
│  │  │ communication skills. Evaluate against this rubric:            │ │    │
│  │  │                                                                 │ │    │
│  │  │ 1. BUSINESS VALUE ARTICULATION (20 pts)                        │ │    │
│  │  │    - Did student quantify impact in business terms?            │ │    │
│  │  │    - Were ROI/metrics clearly stated?                          │ │    │
│  │  │                                                                 │ │    │
│  │  │ 2. AUDIENCE ADAPTATION (20 pts)                                │ │    │
│  │  │    - Did student adjust technical depth appropriately?         │ │    │
│  │  │    - Was jargon avoided or explained?                          │ │    │
│  │  │                                                                 │ │    │
│  │  │ 3. HANDLING OBJECTIONS (15 pts)                                │ │    │
│  │  │    - Did student address concerns constructively?              │ │    │
│  │  │    - Were counter-arguments acknowledged?                      │ │    │
│  │  │                                                                 │ │    │
│  │  │ 4. CLARITY & STRUCTURE (15 pts)                                │ │    │
│  │  │ 5. HONESTY & LIMITATIONS (15 pts)                              │ │    │
│  │  │ 6. ACTIONABLE RECOMMENDATIONS (15 pts)                         │ │    │
│  │  │                                                                 │ │    │
│  │  │ Return JSON with this EXACT structure:                         │ │    │
│  │  │ {                                                               │ │    │
│  │  │   "criteria_scores": {...},                                    │ │    │
│  │  │   "overall_feedback": "...",                                   │ │    │
│  │  │   "strengths": [...],                                          │ │    │
│  │  │   "areas_for_improvement": [...],                              │ │    │
│  │  │   "confidence": 0.0-1.0                                        │ │    │
│  │  │ }                                                               │ │    │
│  │  └────────────────────────────────────────────────────────────────┘ │    │
│  │                                                                      │    │
│  │  ┌────────────────────────────────────────────────────────────────┐ │    │
│  │  │ USER MESSAGE                                                    │ │    │
│  │  │                                                                 │ │    │
│  │  │ CONVERSATION TRANSCRIPT:                                        │ │    │
│  │  │ [STAKEHOLDER]: Good morning. I have 15 minutes...              │ │    │
│  │  │ [STUDENT]: Thank you for meeting with me...                    │ │    │
│  │  │ [STAKEHOLDER]: Interesting. What's the expected ROI?           │ │    │
│  │  │ [STUDENT]: Based on our analysis, we project...                │ │    │
│  │  │ ...                                                             │ │    │
│  │  └────────────────────────────────────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    OUTPUT JSON STRUCTURE                             │    │
│  │                                                                      │    │
│  │  {                                                                   │    │
│  │    "criteria_scores": {                                              │    │
│  │      "business_value_articulation": {                                │    │
│  │        "score": 16,                                                  │    │
│  │        "max_score": 20,                                              │    │
│  │        "evidence": "Student stated '15% revenue increase'...",      │    │
│  │        "feedback": "Good quantification. Consider adding..."        │    │
│  │      },                                                              │    │
│  │      "audience_adaptation": { ... },                                 │    │
│  │      ...                                                             │    │
│  │    },                                                                │    │
│  │    "overall_feedback": "Strong presentation with clear...",         │    │
│  │    "strengths": [                                                    │    │
│  │      "Clear ROI articulation",                                       │    │
│  │      "Professional tone throughout"                                  │    │
│  │    ],                                                                │    │
│  │    "areas_for_improvement": [                                        │    │
│  │      "Address technical risks earlier",                              │    │
│  │      "Provide more specific timelines"                               │    │
│  │    ],                                                                │    │
│  │    "confidence": 0.85  ◄── AI self-assessment                       │    │
│  │  }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Prompt Engineering Deep Dive

### Persona Prompt Anatomy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PERSONA PROMPT COMPONENTS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 1. ROLE ASSIGNMENT                                                   │    │
│  │    "You are Victoria Chen, Chief Executive Officer"                  │    │
│  │                                                                      │    │
│  │    WHY: Establishes identity and authority level                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 2. BACKGROUND CONTEXT                                                │    │
│  │    "Former management consultant at McKinsey, MBA from Wharton,     │    │
│  │     15 years in tech industry, known for data-driven decisions"     │    │
│  │                                                                      │    │
│  │    WHY: Informs knowledge level and decision-making style           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 3. PERSONALITY TRAITS                                                │    │
│  │    - Direct and time-conscious                                       │    │
│  │    - Values clarity over comprehensiveness                           │    │
│  │    - Skeptical of unsubstantiated claims                             │    │
│  │                                                                      │    │
│  │    WHY: Shapes response tone and interaction patterns                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 4. KEY CONCERNS (Role-Specific)                                      │    │
│  │    - "What's the ROI and payback period?"                            │    │
│  │    - "How does this affect our competitive position?"                │    │
│  │    - "What resources are required?"                                  │    │
│  │                                                                      │    │
│  │    WHY: Drives the questions and objections the AI will raise        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 5. BEHAVIORAL INSTRUCTIONS                                           │    │
│  │    - Stay completely in character                                    │    │
│  │    - React authentically based on personality                        │    │
│  │    - Push back on vague or unsupported claims                        │    │
│  │    - Keep responses concise (2-4 sentences)                          │    │
│  │    - Never acknowledge being an AI                                   │    │
│  │                                                                      │    │
│  │    WHY: Ensures consistent, realistic behavior                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ 6. MEETING CONTEXT                                                   │    │
│  │    "The student is presenting a customer churn prediction model     │    │
│  │     they built for the marketing team"                               │    │
│  │                                                                      │    │
│  │    WHY: Grounds the conversation in a specific scenario              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The 6 Personas and Their AI Behaviors

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PERSONA DIFFICULTY MATRIX                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  EASY ────────────────────────────────────────────────────────────── HARD   │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   MARCUS     │  │   PRIYA      │  │   JAMES      │  │  VICTORIA    │    │
│  │   JOHNSON    │  │   SHARMA     │  │   WILSON     │  │    CHEN      │    │
│  │              │  │              │  │              │  │              │    │
│  │  Product     │  │  Technical   │  │    CFO       │  │    CEO       │    │
│  │  Manager     │  │  Lead        │  │              │  │              │    │
│  │              │  │              │  │              │  │              │    │
│  │ • Supportive │  │ • Detail-    │  │ • Cost-      │  │ • Time-      │    │
│  │ • Feature-   │  │   oriented   │  │   focused    │  │   pressured  │    │
│  │   focused    │  │ • Technical  │  │ • ROI-driven │  │ • Strategic  │    │
│  │ • User-      │  │   questions  │  │ • Risk-      │  │ • Skeptical  │    │
│  │   centric    │  │ • Validates  │  │   averse     │  │ • Direct     │    │
│  │              │  │   approach   │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                              │
│        ┌──────────────┐                       ┌──────────────┐              │
│        │   SARAH      │                       │   MICHAEL    │              │
│        │   MARTINEZ   │                       │   CHANG      │              │
│        │              │                       │              │              │
│        │   VP Sales   │                       │  VP Eng.     │              │
│        │              │                       │              │              │
│        │ • Results-   │                       │ • Skeptical  │              │
│        │   oriented   │                       │   of AI hype │              │
│        │ • Customer-  │                       │ • Technical  │              │
│        │   focused    │                       │   depth req. │              │
│        │ • Practical  │                       │ • Maintenance│              │
│        │   adoption   │                       │   concerns   │              │
│        └──────────────┘                       └──────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## AI Design Patterns Used

### Pattern 1: System Prompt Injection

```
┌─────────────────────────────────────────────────────────────┐
│                 SYSTEM PROMPT INJECTION                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Problem: How to make the LLM consistently behave as a       │
│           specific character with defined traits?            │
│                                                              │
│  Solution: Inject detailed persona information in the        │
│            system prompt, which Claude treats as its         │
│            "identity" for the conversation.                  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                API Call Structure                    │    │
│  │                                                      │    │
│  │  {                                                   │    │
│  │    "model": "claude-sonnet-4-20250514",             │    │
│  │    "system": "<PERSONA PROMPT HERE>",  ◄── Identity │    │
│  │    "messages": [                                     │    │
│  │      {"role": "user", "content": "..."}             │    │
│  │    ]                                                 │    │
│  │  }                                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Key Insight: System prompts are processed before user       │
│               messages and establish behavioral context.     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 2: Conversation Memory Management

```
┌─────────────────────────────────────────────────────────────┐
│              CONVERSATION MEMORY MANAGEMENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Problem: LLMs are stateless - each API call is independent. │
│           How do we maintain conversation context?           │
│                                                              │
│  Solution: Include full message history in each API call.    │
│                                                              │
│  Turn 1:                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ messages: [                                          │    │
│  │   {role: "user", content: "Hi, I'm presenting..."}  │    │
│  │ ]                                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Turn 2:                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ messages: [                                          │    │
│  │   {role: "user", content: "Hi, I'm presenting..."},  │   │
│  │   {role: "assistant", content: "Good morning..."},   │   │
│  │   {role: "user", content: "The model predicts..."}  │    │
│  │ ]                                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Turn 3:                                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ messages: [                                          │    │
│  │   ... all previous messages ...                      │    │
│  │   {role: "user", content: "ROI is estimated at..."}  │   │
│  │ ]                                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Trade-off: Token usage grows with conversation length.      │
│             For long conversations, may need summarization.  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 3: Structured Output with JSON

```
┌─────────────────────────────────────────────────────────────┐
│              STRUCTURED OUTPUT GENERATION                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Problem: LLM outputs are freeform text. How do we get       │
│           reliable, parseable structured data?               │
│                                                              │
│  Solution: Explicit JSON schema in prompt + robust parsing.  │
│                                                              │
│  Technique 1: Provide exact schema                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ "Return a JSON object with this EXACT structure:     │    │
│  │  {                                                   │    │
│  │    'score': <number 0-100>,                         │    │
│  │    'feedback': '<string>',                          │    │
│  │    'evidence': ['<quote1>', '<quote2>']             │    │
│  │  }"                                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Technique 2: Lower temperature for consistency              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ temperature = 0.3  # vs 0.7 for conversation         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Technique 3: Robust parsing with fallbacks                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ def parse_json(response):                            │    │
│  │     # Handle markdown code blocks                    │    │
│  │     if "```json" in response:                        │    │
│  │         json_str = response.split("```json")[1]      │    │
│  │         json_str = json_str.split("```")[0]          │    │
│  │     try:                                             │    │
│  │         return json.loads(json_str)                  │    │
│  │     except:                                          │    │
│  │         return {"error": "parse_failed"}             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 4: Confidence Scoring for Quality Control

```
┌─────────────────────────────────────────────────────────────┐
│              CONFIDENCE-BASED QUALITY CONTROL                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Problem: AI evaluations aren't always reliable. How do we   │
│           know when to trust the AI vs. involve humans?      │
│                                                              │
│  Solution: Ask the AI to self-assess its confidence.         │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Prompt includes:                                     │    │
│  │ "Also provide a confidence score (0.0-1.0)           │    │
│  │  indicating how certain you are of this evaluation.  │    │
│  │  Lower confidence if:                                │    │
│  │  - Conversation was very short                       │    │
│  │  - Student responses were ambiguous                  │    │
│  │  - Criteria were hard to evaluate"                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Routing Logic:                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │    confidence >= 0.7  ──────>  Auto-accept grade    │    │
│  │                                                      │    │
│  │    confidence < 0.7   ──────>  Flag for instructor  │    │
│  │                                 review               │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Result: Human-in-the-loop for edge cases only.             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 5: Evidence-Based Evaluation

```
┌─────────────────────────────────────────────────────────────┐
│              EVIDENCE-BASED EVALUATION                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Problem: AI scores without justification are not            │
│           actionable or verifiable.                          │
│                                                              │
│  Solution: Require specific quotes/observations as evidence. │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Prompt requirement:                                  │    │
│  │ "For each criterion, provide:                        │    │
│  │  - score: numeric score                              │    │
│  │  - evidence: specific quote or observation           │    │
│  │  - feedback: actionable improvement suggestion"      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Example output:                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ "business_value_articulation": {                     │    │
│  │   "score": 16,                                       │    │
│  │   "evidence": "Student said 'This model will reduce │    │
│  │                churn by 15%, saving $2M annually'",  │    │
│  │   "feedback": "Strong quantification. Consider       │    │
│  │                adding payback period calculation."   │    │
│  │ }                                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Benefits:                                                   │
│  - Students see exactly what was evaluated                   │
│  - Instructors can verify AI reasoning                       │
│  - Feedback is specific and actionable                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow & State Management

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE REQUEST FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. USER SENDS MESSAGE                                                       │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  POST /api/v1/conversations/{id}/messages                        │     │
│     │  Body: { "content": "I'd like to present our ML model..." }     │     │
│     └───────────────────────────────┬─────────────────────────────────┘     │
│                                     │                                        │
│                                     ▼                                        │
│  2. API VALIDATES & LOADS STATE                                              │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  • Verify user owns conversation                                 │     │
│     │  • Load conversation from PostgreSQL                             │     │
│     │  • Load all previous messages                                    │     │
│     │  • Load scenario → persona details                               │     │
│     └───────────────────────────────┬─────────────────────────────────┘     │
│                                     │                                        │
│                                     ▼                                        │
│  3. CONVERSATION ENGINE PROCESSES                                            │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  • Build system prompt from persona                              │     │
│     │  • Convert messages to Claude format                             │     │
│     │  • Add new user message to history                               │     │
│     └───────────────────────────────┬─────────────────────────────────┘     │
│                                     │                                        │
│                                     ▼                                        │
│  4. LLM CLIENT CALLS CLAUDE API                                              │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  POST https://api.anthropic.com/v1/messages                      │     │
│     │  {                                                               │     │
│     │    "model": "claude-sonnet-4-20250514",                         │     │
│     │    "max_tokens": 500,                                            │     │
│     │    "temperature": 0.7,                                           │     │
│     │    "system": "<persona prompt>",                                 │     │
│     │    "messages": [<full conversation history>]                     │     │
│     │  }                                                               │     │
│     └───────────────────────────────┬─────────────────────────────────┘     │
│                                     │                                        │
│                                     ▼                                        │
│  5. RESPONSE PROCESSING                                                      │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  • Extract response text from Claude                             │     │
│     │  • Save student message to database                              │     │
│     │  • Save stakeholder response to database                         │     │
│     │  • Increment turn count                                          │     │
│     │  • Check if should end (max turns reached)                       │     │
│     └───────────────────────────────┬─────────────────────────────────┘     │
│                                     │                                        │
│                                     ▼                                        │
│  6. RETURN TO CLIENT                                                         │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  {                                                               │     │
│     │    "student_message": {...},                                     │     │
│     │    "stakeholder_message": {...},                                 │     │
│     │    "turn_count": 5,                                              │     │
│     │    "should_end": false                                           │     │
│     │  }                                                               │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quality Assurance & Reliability

### Error Handling Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING STRATEGY                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Layer 1: LLM Client                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • API timeout handling (30s default)                                │    │
│  │  • Rate limit detection and retry                                    │    │
│  │  • Invalid response format handling                                  │    │
│  │  • Connection error recovery                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 2: JSON Parsing                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Handle markdown code block wrappers                               │    │
│  │  • Strip whitespace and control characters                           │    │
│  │  • Fallback to error object on parse failure                         │    │
│  │  • Log failures for debugging                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Layer 3: Business Logic                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  • Validate score ranges (0-100)                                     │    │
│  │  • Ensure required fields present                                    │    │
│  │  • Default values for missing optional fields                        │    │
│  │  • Flag incomplete grades for review                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Human-in-the-Loop Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HUMAN-IN-THE-LOOP WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                     ┌──────────────────┐                                     │
│                     │  AI Grades       │                                     │
│                     │  Conversation    │                                     │
│                     └────────┬─────────┘                                     │
│                              │                                               │
│                              ▼                                               │
│                     ┌──────────────────┐                                     │
│                     │  Confidence      │                                     │
│                     │  Check           │                                     │
│                     └────────┬─────────┘                                     │
│                              │                                               │
│              ┌───────────────┴───────────────┐                               │
│              │                               │                               │
│              ▼                               ▼                               │
│     ┌──────────────────┐          ┌──────────────────┐                      │
│     │  confidence      │          │  confidence      │                      │
│     │  >= 0.7          │          │  < 0.7           │                      │
│     └────────┬─────────┘          └────────┬─────────┘                      │
│              │                             │                                 │
│              ▼                             ▼                                 │
│     ┌──────────────────┐          ┌──────────────────┐                      │
│     │  Auto-Accept     │          │  Flag for        │                      │
│     │  Grade           │          │  Review          │                      │
│     └────────┬─────────┘          └────────┬─────────┘                      │
│              │                             │                                 │
│              │                             ▼                                 │
│              │                    ┌──────────────────┐                      │
│              │                    │  Instructor      │                      │
│              │                    │  Reviews         │                      │
│              │                    └────────┬─────────┘                      │
│              │                             │                                 │
│              │              ┌──────────────┴──────────────┐                 │
│              │              │                             │                 │
│              │              ▼                             ▼                 │
│              │     ┌──────────────────┐        ┌──────────────────┐        │
│              │     │  Approve         │        │  Override        │        │
│              │     │  AI Grade        │        │  with New Grade  │        │
│              │     └────────┬─────────┘        └────────┬─────────┘        │
│              │              │                           │                   │
│              └──────────────┴───────────────────────────┘                   │
│                              │                                               │
│                              ▼                                               │
│                     ┌──────────────────┐                                     │
│                     │  Final Grade     │                                     │
│                     │  Stored          │                                     │
│                     └──────────────────┘                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Learnings

### What Worked Well

| Technique | Why It Worked |
|-----------|---------------|
| **Detailed persona prompts** | Rich backgrounds produced consistent, believable characters |
| **Lower temperature for grading** | 0.3 vs 0.7 significantly improved JSON output reliability |
| **Evidence requirements** | Forced AI to ground evaluations in specific observations |
| **Confidence scoring** | Effective proxy for when to involve human review |
| **Role-specific concerns** | Made each persona feel distinct and realistic |

### Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Persona breaking character** | Added explicit "Never acknowledge being an AI" instruction |
| **Inconsistent JSON format** | Provided exact schema + handled markdown wrappers in parser |
| **Overly long responses** | Set max_tokens=500 and added "Keep responses concise" instruction |
| **Grading too generous** | Added specific rubric criteria with point values |
| **Context loss in long conversations** | Included full message history (watch token limits) |

### Production Considerations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCTION CONSIDERATIONS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Cost Management                                                             │
│  ├── Track token usage per conversation                                      │
│  ├── Set per-user daily limits                                               │
│  ├── Consider caching for repeated grading requests                          │
│  └── Use smaller model for simple tasks (haiku for coaching hints)          │
│                                                                              │
│  Latency Optimization                                                        │
│  ├── Stream responses for real-time chat feel                                │
│  ├── Pre-warm persona prompts                                                │
│  ├── Consider edge caching for static content                                │
│  └── Async processing for grading (non-blocking)                             │
│                                                                              │
│  Reliability                                                                 │
│  ├── Implement retry with exponential backoff                                │
│  ├── Circuit breaker for API failures                                        │
│  ├── Fallback responses for degraded mode                                    │
│  └── Queue system for grade processing                                       │
│                                                                              │
│  Monitoring                                                                  │
│  ├── Track API latency and error rates                                       │
│  ├── Log prompt/response pairs for debugging                                 │
│  ├── Alert on confidence score trends                                        │
│  └── Monitor token usage and costs                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

StakeholderSim demonstrates production-grade AI engineering through:

1. **Prompt Engineering Excellence** - Carefully crafted persona and grading prompts
2. **Robust State Management** - Proper conversation history handling
3. **Structured Output Reliability** - JSON parsing with fallbacks
4. **Quality Control Systems** - Confidence scoring and human-in-the-loop
5. **Evidence-Based AI** - Grounded evaluations with citations

These patterns are transferable to any LLM-based application requiring consistent behavior, reliable structured outputs, and appropriate human oversight.

---

*Document generated for StakeholderSim - December 2024*
