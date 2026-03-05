# StakeholderSim — Pilot Feature PRD

## Context

This document extends the existing PRD (`stakeholder_sim_prd.md`) and should be read alongside the full codebase. It defines four features required before the first real student pilot can run. Implement them in the order listed. Do not move to the next feature until the current one is working end-to-end.

The existing codebase has a working conversation engine, grading engine, LLM integration, persona system, and instructor dashboard. The primary gaps are real authentication, screen lock enforcement, and session time tracking. The architecture is solid — do not refactor what is already working unless a specific feature requires it.

---

## Feature 1: Real Authentication

### Problem
Auth is currently mocked with four hardcoded users in `backend/app/routers/auth.py`. There is no signup, no real identity, and no way to tie a conversation to an actual student. This must be replaced before any real pilot.

### Requirements

**Backend**
- Email and password signup and login
- Passwords hashed with bcrypt
- JWT tokens structured as currently implemented, backed by real DB users
- Keep the existing role system: `student`, `instructor`, `admin`
- Wire to the existing `User` model in `backend/app/models/user.py` — extend it if needed
- Add a proper Alembic migration for any schema changes
- Retain a seed script that creates test users with known credentials for development use

**Frontend**
- Replace the mock user key selector on the login page with email and password fields
- Standard login and signup flows
- Errors handled clearly (wrong password, email not found, etc.)

**Seed credentials (print to console on seed completion)**
- 2 instructor accounts
- 5 student accounts
- Format: `role | email | password`

---

## Feature 2: Screen Lock

### Problem
Students in an active chat session must stay focused on the conversation. Accidental tab switches happen and should not be penalized the same as deliberate ones. The system needs a graduated escalation that is fair but firm.

### Requirements

**Trigger events**
- `document.visibilitychange` (tab switch or window minimize)
- `window.blur` (focus lost to another application)
- Do not trigger on the first page load

**Escalation logic**

| Switch # | Response | Timer | Logged to backend |
|----------|----------|-------|-------------------|
| 1st | Soft toast notification at bottom of screen: "Please stay on this page." Session continues. | Keeps running | Yes |
| 2nd | Modal overlay. Student must click to acknowledge before continuing. | Pauses until acknowledged | Yes |
| 3rd | Hard modal with explicit message: "Warning: one more violation will automatically submit your session." Student must acknowledge. | Pauses until acknowledged | Yes |
| 4th | Auto-submit conversation immediately. Session closes. Conversation enters grading queue. Student sees "Session Terminated" screen with submission confirmation. | Stopped, timestamp recorded | Yes |

**Session state**
- Violation counter lives in frontend state and syncs to backend on each violation
- Each violation event logged with: violation number, timestamp, current turn number
- On auto-submit (4th violation): record exact timestamp and turn number

**Instructor visibility**
- Violation count and violation log visible in the instructor grade review view alongside the transcript
- A student with 3 violations should be visually distinguishable from one with 0

**Scope**
- Screen lock only activates on the active chat page: `frontend/src/app/chat/[id]/page.tsx`
- Does not activate on dashboard, assignments, history, or instructor pages

---

## Feature 3: Session Time Tracking

### Problem
There is currently no way to know how long a student spent on a session, whether they rushed through it or took their time, or how much of that time was active versus paused.

### Requirements

**Track the following per conversation**
- `started_at`: timestamp when the student sends their first message
- `ended_at`: timestamp when the session ends (natural completion or auto-submit)
- `total_active_seconds`: wall time minus any paused periods (pauses occur during modal acknowledgments on 2nd and 3rd violations)
- `violation_log`: array of `{ violation_number, timestamp, turn_number }`

**Backend**
- Add these fields to the Conversation model
- Add Alembic migration
- Expose them in the existing conversation and grade response schemas

**Instructor dashboard**
- Show session duration and active time on the grade review page
- Format as minutes and seconds, not raw timestamps

---

## Feature 4: Migrations and Seed Data

### Requirements

- Generate clean Alembic migration files for all schema changes introduced in Features 1, 2, and 3
- Migrations must run cleanly from scratch with `alembic upgrade head`
- Update the seed script to create:
  - 2 instructor accounts
  - 5 student accounts
  - 1 course
  - 2 assignments linked to that course
  - All existing personas and scenarios
- Print all seed credentials to console on completion

---

## Verification Checklist

After all four features are complete, verify the following end-to-end flow:

- [ ] Student signs up with email and password
- [ ] Student logs in and sees their assignments
- [ ] Student enters a chat session
- [ ] Tab switch triggers soft warning (1st)
- [ ] Second tab switch shows acknowledgment modal and pauses timer
- [ ] Third tab switch shows hard warning modal
- [ ] Fourth tab switch auto-submits session and shows termination screen
- [ ] Instructor logs in and sees the student's completed session
- [ ] Grade review shows: score, rubric breakdown, violation count and log, session duration
- [ ] `docker compose up` starts cleanly with `alembic upgrade head` and seed script

---

## Out of Scope for This Sprint

- LMS integration
- Streaming responses
- Voice input
- Custom rubric builder
- Any changes to the persona prompts or grading rubric criteria
- Any frontend redesign beyond what the new features require
