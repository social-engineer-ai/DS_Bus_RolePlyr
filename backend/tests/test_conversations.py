"""Tests for conversation endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app

client = TestClient(app)

# Test scenario ID from seed data
TEST_SCENARIO_ID = "88888881-8888-8888-8888-888888888888"


class TestConversationEndpoints:
    """Tests for conversation API endpoints."""

    def test_list_scenarios(self):
        """Test listing available scenarios."""
        response = client.get("/api/v1/conversations/scenarios?user_key=student1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_conversations_empty(self):
        """Test listing conversations when none exist."""
        response = client.get("/api/v1/conversations?user_key=student1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_start_conversation_missing_context(self):
        """Test starting conversation without required context."""
        response = client.post(
            "/api/v1/conversations?user_key=student1",
            json={
                "scenario_id": TEST_SCENARIO_ID,
                "context": "",  # Empty context
            },
        )
        assert response.status_code == 422  # Validation error

    def test_start_conversation_invalid_scenario(self):
        """Test starting conversation with invalid scenario."""
        response = client.post(
            "/api/v1/conversations?user_key=student1",
            json={
                "scenario_id": "00000000-0000-0000-0000-000000000000",
                "context": "Test project description for my ML model",
            },
        )
        assert response.status_code == 404

    def test_get_nonexistent_conversation(self):
        """Test getting a conversation that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/v1/conversations/{fake_id}?user_key=student1")
        assert response.status_code == 404

    def test_send_message_nonexistent_conversation(self):
        """Test sending message to nonexistent conversation."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/v1/conversations/{fake_id}/messages?user_key=student1",
            json={"content": "Test message"},
        )
        assert response.status_code == 404


class TestConversationEngine:
    """Tests for conversation engine logic."""

    def test_persona_prompt_building(self):
        """Test that persona prompts are built correctly."""
        from app.services.conversation_engine import ConversationEngine
        from app.models.persona import Persona

        # Create mock persona
        persona = MagicMock(spec=Persona)
        persona.to_prompt_context.return_value = {
            "name": "Patricia Chen",
            "title": "VP of Talent Acquisition",
            "background": "8 years at the company",
            "personality": "Skeptical but fair",
            "concerns": ["ROI", "Candidate experience"],
            "required_questions": ["How much time will this save?"],
        }

        engine = ConversationEngine(
            persona=persona,
            context="Test ML model for resume screening",
        )

        prompt = engine.build_system_prompt()

        # Verify prompt contains key elements
        assert "Patricia Chen" in prompt
        assert "VP of Talent Acquisition" in prompt
        assert "ROI" in prompt
        assert "resume screening" in prompt
        assert "Stay in character" in prompt

    def test_message_history_loading(self):
        """Test loading message history."""
        from app.services.conversation_engine import ConversationEngine
        from app.models.conversation import Message, MessageRole

        persona = MagicMock()
        persona.to_prompt_context.return_value = {
            "name": "Test",
            "title": "Test",
            "background": "",
            "personality": "",
            "concerns": [],
            "required_questions": [],
        }

        engine = ConversationEngine(persona=persona, context="Test")

        # Create mock messages
        messages = [
            MagicMock(role=MessageRole.STAKEHOLDER, content="Hello"),
            MagicMock(role=MessageRole.STUDENT, content="Hi there"),
        ]

        engine.load_history(messages)

        assert len(engine.history) == 2
        assert engine.history[0]["role"] == "assistant"  # stakeholder
        assert engine.history[1]["role"] == "user"  # student

    def test_should_end_conversation(self):
        """Test conversation ending logic."""
        from app.services.conversation_engine import ConversationEngine

        persona = MagicMock()
        persona.to_prompt_context.return_value = {
            "name": "Test",
            "title": "Test",
            "background": "",
            "personality": "",
            "concerns": [],
            "required_questions": [],
        }

        engine = ConversationEngine(persona=persona, context="Test")

        # Should not end at turn 5
        assert not engine.should_end_conversation(5, 15)

        # Should end at turn 15
        assert engine.should_end_conversation(15, 15)

        # Should end past max
        assert engine.should_end_conversation(20, 15)


class TestLLMClient:
    """Tests for LLM client wrapper."""

    def test_client_initialization_no_key(self):
        """Test client fails without API key."""
        from app.services.llm_client import LLMClient

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                # Force reload of settings
                from app.config import Settings
                settings = Settings(anthropic_api_key="")
                LLMClient(api_key="")
