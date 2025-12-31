# Session Notes: Phase 2 - Conversation Engine

**Date:** 2024-12-31
**Phase:** Phase 2 - Core Conversation Engine (Weeks 3-4)

## What We Accomplished

### Claude API Integration
- Created `LLMClient` wrapper for Anthropic Claude API
- Configured for claude-sonnet-4-20250514 model
- Support for both text and JSON responses
- Singleton pattern for efficient connection reuse

### Conversation Engine
- Built `ConversationEngine` class with full persona prompt support
- Dynamic system prompt generation from persona data
- Conversation history management
- Opening message generation
- Response generation with context
- Closing message generation
- Turn-based conversation ending logic

### API Endpoints
Created full conversation API at `/api/v1/conversations`:
- `GET /scenarios` - List available practice scenarios
- `POST /` - Start new conversation (generates opening message)
- `GET /{id}` - Get conversation with message history
- `POST /{id}/messages` - Send message & get AI response
- `POST /{id}/end` - End conversation (generates closing message)
- `GET /` - List user's conversations

### Frontend Chat Interface
- **Home Page** - Landing page with system status and navigation
- **Scenarios Page** - List/select scenarios with modal for project description
- **Chat Page** - Real-time chat interface with:
  - Message display (student/stakeholder differentiated)
  - Auto-scroll to latest messages
  - Typing indicator during AI response
  - Turn count and status display
  - End conversation button
  - Context display bar
- **History Page** - List past conversations with status/scores

### Pydantic Schemas
Created comprehensive request/response schemas:
- `StartConversationRequest`, `SendMessageRequest`
- `ConversationResponse`, `ConversationListItem`
- `MessageResponse`, `StakeholderMessageResponse`
- `EndConversationResponse`, `ScenarioResponse`

### Tests
- Endpoint validation tests
- Conversation engine unit tests
- LLM client initialization tests

## Files Created

### Backend Services
- `backend/app/services/llm_client.py` - Claude API wrapper
- `backend/app/services/conversation_engine.py` - Conversation logic

### Backend Schemas
- `backend/app/schemas/conversation.py` - Pydantic models

### Backend Routers
- `backend/app/routers/conversations.py` - API endpoints

### Frontend
- `frontend/src/lib/api.ts` - API client
- `frontend/src/components/ChatMessage.tsx`
- `frontend/src/components/ChatInput.tsx`
- `frontend/src/components/ScenarioCard.tsx`
- `frontend/src/app/page.tsx` - Updated home page
- `frontend/src/app/scenarios/page.tsx` - Scenario selection
- `frontend/src/app/chat/[id]/page.tsx` - Chat interface
- `frontend/src/app/history/page.tsx` - Conversation history

### Tests
- `backend/tests/test_conversations.py`

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Model | claude-sonnet-4-20250514 | Balance of quality and cost |
| Response Temperature | 0.7 for chat, 0.3 for JSON | Natural variation for chat, consistency for structured output |
| Max Tokens | 400 for responses | Concise stakeholder responses |
| History Loading | Full history per request | Maintains context across turns |

## API Flow

```
1. Student selects scenario → GET /scenarios
2. Student enters project description → POST / (creates conversation)
3. System returns opening message from stakeholder
4. Student sends message → POST /{id}/messages
5. System returns stakeholder response
6. Repeat 4-5 until max turns or student ends
7. Student ends → POST /{id}/end
8. System returns closing message
9. (Phase 3) System triggers grading
```

## Testing the Flow

```bash
# 1. Start services
make run

# 2. Seed database (if not done)
make seed

# 3. Access frontend
open http://localhost:3000

# 4. Click "Start Practicing"
# 5. Select a persona
# 6. Enter project description
# 7. Have a conversation!
```

## What's Next (Phase 3)

### Grading System
1. **Grading Engine** - Claude-based evaluation against rubric
2. **Grading Prompts** - Engineering prompts for consistent scoring
3. **Grade Storage** - Save grades with criteria breakdown
4. **Grade UI** - Display scores and feedback to students
5. **Instructor Override** - Allow manual grade adjustments

---

*Phase 2 complete. Conversation engine is functional and ready for grading integration.*
