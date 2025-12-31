# StakeholderSim

AI-powered role-play training platform for data science students to practice presenting to business stakeholders.

## What It Does

StakeholderSim provides a safe environment for students to practice high-stakes business conversations:

- **6 AI Stakeholder Personas** - CEO, CFO, VP of Engineering, Product Manager, and more - each with unique personalities and concerns
- **Real-time Conversations** - Natural dialogue powered by Claude AI that responds contextually
- **Automated Grading** - AI evaluates against a 6-criteria professional rubric (100 points)
- **Progress Tracking** - Students see improvement over time with detailed feedback
- **Instructor Dashboard** - Class analytics, grade review, and assignment management

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

```bash
# Clone the repository
git clone https://github.com/social-engineer-ai/DS_Bus_RolePlyr.git
cd DS_Bus_RolePlyr

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Build and start (first time)
docker compose build
docker compose up -d db redis
sleep 5
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.scripts.seed
docker compose up -d

# Or if make works on your system:
# make setup && make run
```

### Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend application |
| http://localhost:8000/docs | API documentation |
| http://localhost:8000 | Backend API |

### Test Users (Mock Auth)

| User Key | Role | Use For |
|----------|------|---------|
| `student1` | Student | Practice, assignments, dashboard |
| `student2` | Student | Practice, assignments, dashboard |
| `instructor` | Instructor | Class management, grade review |

Access instructor view: http://localhost:3000/instructor

## Project Structure

```
├── backend/                 # Python/FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Business logic (LLM, grading, etc.)
│   │   └── scripts/        # Database seeding
│   ├── alembic/            # Database migrations
│   └── tests/
├── frontend/               # Next.js 14 frontend
│   └── src/
│       ├── app/            # Pages (App Router)
│       ├── components/     # React components
│       └── lib/            # API client, utilities
├── docs/                   # Documentation
└── docker-compose.yml      # Container orchestration
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic 2.0 |
| Database | PostgreSQL 15, Redis 7 |
| AI/LLM | Claude API (claude-sonnet-4-20250514) |
| Infrastructure | Docker, Docker Compose |

## Key Features

### For Students
- **Unlimited Practice** - No embarrassment, no judgment
- **Realistic Scenarios** - Present ML models, dashboards, analyses
- **Instant Feedback** - Detailed scoring on 6 criteria
- **Progress Tracking** - See improvement over time

### For Instructors
- **Assignment Management** - Create assignments with due dates
- **Class Analytics** - Score distributions, common struggles
- **Grade Review** - Override AI grades when needed
- **Student Monitoring** - Track who needs attention

### Grading Rubric (100 points)

| Criterion | Points | What It Measures |
|-----------|--------|------------------|
| Business Value | 20 | Quantifying impact in business terms |
| Audience Adaptation | 20 | Adjusting technical depth appropriately |
| Handling Objections | 15 | Responding to pushback constructively |
| Clarity & Structure | 15 | Organized, clear communication |
| Honesty & Limitations | 15 | Acknowledging constraints and risks |
| Actionable Recommendations | 15 | Clear next steps and asks |

## Documentation

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete technical documentation
  - Architecture deep-dive
  - AI Engineering concepts explained
  - Enhancement opportunities
  - Learning resources

- **[docs/PRE_DEPLOYMENT_CHECKLIST.md](docs/PRE_DEPLOYMENT_CHECKLIST.md)** - Production readiness checklist

- **[stakeholder_sim_prd.md](stakeholder_sim_prd.md)** - Original product requirements

## Development Commands

```bash
# Start/stop services
docker compose up -d          # Start all services
docker compose down           # Stop all services
docker compose logs -f        # View logs

# Database
docker compose run --rm backend alembic upgrade head    # Run migrations
docker compose run --rm backend python -m app.scripts.seed  # Seed data
docker compose exec db psql -U stakeholder_sim -d stakeholder_sim  # DB shell

# Testing
docker compose exec backend pytest -v      # Run tests
docker compose exec frontend npm test      # Frontend tests
```

## AI Engineering Highlights

This project demonstrates several key AI engineering patterns:

1. **Prompt Engineering** - Persona system prompts, grading prompts, structured outputs
2. **Conversation State Management** - Maintaining context across turns
3. **LLM API Integration** - Proper error handling, temperature tuning
4. **AI Confidence Scoring** - Self-assessment for quality control
5. **Human-in-the-Loop** - Instructor review for low-confidence grades

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed explanations with code examples.

## Roadmap / Enhancement Ideas

- [ ] Voice mode (speech-to-text input)
- [ ] Real-time streaming responses
- [ ] Custom rubric builder
- [ ] LMS integration (Canvas, Blackboard)
- [ ] Multi-language support
- [ ] Video avatar personas
- [ ] Peer review system

## Authentication Warning

> **This MVP uses mock authentication for development.**
> Before deploying to production, implement real OAuth 2.0 authentication.
> See [PRE_DEPLOYMENT_CHECKLIST.md](docs/PRE_DEPLOYMENT_CHECKLIST.md).

## License

MIT License - See LICENSE file for details.

---

Built with Claude Code | December 2024
