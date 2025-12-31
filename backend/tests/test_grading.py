"""Tests for grading functionality."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestGradingEndpoints:
    """Tests for grading API endpoints."""

    def test_get_grade_not_found(self):
        """Test getting grade for nonexistent conversation."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/grades/conversations/{fake_id}?user_key=student1"
        )
        assert response.status_code == 404

    def test_trigger_grading_conversation_not_found(self):
        """Test triggering grading for nonexistent conversation."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/v1/grades/conversations/{fake_id}/grade?user_key=student1",
            json={"force": False},
        )
        assert response.status_code == 404

    def test_override_grade_requires_instructor(self):
        """Test that grade override requires instructor role."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/v1/grades/conversations/{fake_id}/override?user_key=student1",
            json={
                "criteria_scores": {"business_value_articulation": 20},
                "reason": "Student showed good improvement",
            },
        )
        assert response.status_code == 403

    def test_needs_review_requires_instructor(self):
        """Test that needs-review endpoint requires instructor role."""
        response = client.get(
            "/api/v1/grades/needs-review?user_key=student1"
        )
        assert response.status_code == 403

    def test_needs_review_accessible_to_instructor(self):
        """Test that instructor can access needs-review."""
        response = client.get(
            "/api/v1/grades/needs-review?user_key=instructor"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGradingEngine:
    """Tests for grading engine logic."""

    def test_format_transcript(self):
        """Test transcript formatting."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric
        from app.models.conversation import Conversation, Message, MessageRole

        rubric = MagicMock(spec=Rubric)
        rubric.criteria = []
        rubric.total_points = 100

        engine = GradingEngine(rubric)

        # Create mock conversation with messages
        conversation = MagicMock(spec=Conversation)
        msg1 = MagicMock()
        msg1.role = MessageRole.STAKEHOLDER
        msg1.content = "Hello, what do you have?"
        msg2 = MagicMock()
        msg2.role = MessageRole.STUDENT
        msg2.content = "I built a model that predicts..."

        conversation.messages = [msg1, msg2]

        transcript = engine._format_transcript(conversation)

        assert "[Turn 1] Stakeholder:" in transcript
        assert "Hello, what do you have?" in transcript
        assert "[Turn 2] Student:" in transcript
        assert "I built a model that predicts..." in transcript

    def test_build_criteria_text(self):
        """Test criteria text building."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric

        rubric = MagicMock(spec=Rubric)
        rubric.criteria = [
            {
                "name": "test_criterion",
                "display_name": "Test Criterion",
                "description": "Test description",
                "max_points": 25,
                "scoring_guide": {
                    "25": "Excellent",
                    "15": "Good",
                    "5": "Poor",
                },
            }
        ]

        engine = GradingEngine(rubric)
        criteria_text = engine._build_criteria_text()

        assert "Test Criterion" in criteria_text
        assert "25 points" in criteria_text
        assert "Excellent" in criteria_text

    def test_parse_grade_response_valid_json(self):
        """Test parsing valid grade response."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric

        rubric = MagicMock(spec=Rubric)
        engine = GradingEngine(rubric)

        response = '''
        {
            "criteria_scores": {
                "test": {"score": 20, "max_score": 25, "evidence": "Good", "feedback": "Keep it up"}
            },
            "total_score": 80,
            "overall_feedback": "Great work",
            "strengths": ["Clear communication"],
            "areas_for_improvement": ["Add more numbers"],
            "confidence": 0.85
        }
        '''

        result = engine._parse_grade_response(response)

        assert result["total_score"] == 80
        assert result["confidence"] == 0.85
        assert "test" in result["criteria_scores"]

    def test_parse_grade_response_with_markdown(self):
        """Test parsing grade response wrapped in markdown."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric

        rubric = MagicMock(spec=Rubric)
        engine = GradingEngine(rubric)

        response = '''
        ```json
        {
            "criteria_scores": {},
            "total_score": 75,
            "overall_feedback": "Good",
            "strengths": [],
            "areas_for_improvement": [],
            "confidence": 0.9
        }
        ```
        '''

        result = engine._parse_grade_response(response)
        assert result["total_score"] == 75

    def test_parse_grade_response_missing_field(self):
        """Test parsing response with missing required field."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric

        rubric = MagicMock(spec=Rubric)
        engine = GradingEngine(rubric)

        response = '{"total_score": 80}'  # Missing other fields

        with pytest.raises(ValueError, match="Missing required field"):
            engine._parse_grade_response(response)

    def test_parse_grade_response_invalid_json(self):
        """Test parsing invalid JSON."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric

        rubric = MagicMock(spec=Rubric)
        engine = GradingEngine(rubric)

        with pytest.raises(ValueError, match="Failed to parse"):
            engine._parse_grade_response("not valid json")

    def test_create_grade_record(self):
        """Test creating Grade model from data."""
        from app.services.grading_engine import GradingEngine
        from app.models.rubric import Rubric
        from app.models.grade import GradedBy

        rubric = MagicMock(spec=Rubric)
        engine = GradingEngine(rubric)

        conversation_id = uuid4()
        rubric_id = uuid4()
        grade_data = {
            "criteria_scores": {"test": {"score": 20}},
            "total_score": 80,
            "overall_feedback": "Good work",
            "strengths": ["Clear"],
            "areas_for_improvement": ["More detail"],
            "confidence": 0.85,
        }

        grade = engine.create_grade_record(conversation_id, rubric_id, grade_data)

        assert grade.conversation_id == conversation_id
        assert grade.rubric_id == rubric_id
        assert grade.total_score == Decimal("80")
        assert grade.graded_by == GradedBy.AI
        assert grade.instructor_override == False
