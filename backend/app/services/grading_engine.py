"""Grading engine for evaluating stakeholder conversations."""

import json
import re
from typing import Optional
from decimal import Decimal

from app.models.conversation import Conversation
from app.models.persona import Persona
from app.models.rubric import Rubric
from app.models.grade import Grade, GradedBy
from app.services.llm_client import get_llm_client, LLMClient


class GradingEngine:
    """Engine for AI-powered grading of stakeholder conversations."""

    def __init__(self, rubric: Rubric, llm_client: Optional[LLMClient] = None):
        """Initialize the grading engine.

        Args:
            rubric: The grading rubric to evaluate against.
            llm_client: Optional LLM client (uses singleton if not provided).
        """
        self.rubric = rubric
        self.llm_client = llm_client or get_llm_client()

    def _format_transcript(self, conversation: Conversation) -> str:
        """Format conversation messages as a readable transcript."""
        lines = []
        for i, msg in enumerate(conversation.messages, 1):
            role = "Student" if msg.role.value == "student" else "Stakeholder"
            lines.append(f"[Turn {i}] {role}:\n{msg.content}")
        return "\n\n".join(lines)

    def _build_criteria_text(self) -> str:
        """Build detailed criteria text for the grading prompt."""
        lines = []
        for criterion in self.rubric.criteria:
            lines.append(f"\n### {criterion['display_name']} ({criterion['max_points']} points)")
            if criterion.get('description'):
                lines.append(f"**Description:** {criterion['description']}")

            if criterion.get('scoring_guide'):
                lines.append("\n**Scoring Guide:**")
                # Sort by score descending
                sorted_guide = sorted(
                    criterion['scoring_guide'].items(),
                    key=lambda x: int(x[0]),
                    reverse=True
                )
                for score, description in sorted_guide:
                    lines.append(f"- {score} points: {description}")

        return "\n".join(lines)

    def _build_grading_prompt(
        self,
        conversation: Conversation,
        persona: Persona,
    ) -> str:
        """Build the system prompt for grading."""
        return f"""You are an expert evaluator assessing a student's ability to communicate with business stakeholders about data science work.

## Your Task
Evaluate the following conversation where a student presented their data science project to a business stakeholder. Grade their performance against the provided rubric.

## Grading Philosophy
- Be fair but rigorous - this is professional training
- Look for specific evidence in the conversation to justify scores
- Consider both what was said and what was missing
- Acknowledge strengths while identifying areas for improvement
- Your goal is to help the student improve, not to be harsh

## The Rubric
{self._build_criteria_text()}

## Total Points Possible: {self.rubric.total_points}

## Context
- **Student's Project:** {conversation.context}
- **Stakeholder:** {persona.name}, {persona.title}
- **Stakeholder Background:** {persona.background or 'Not specified'}
- **Conversation Turns:** {conversation.turn_count}

## The Conversation Transcript
{self._format_transcript(conversation)}

## Your Evaluation
Evaluate the conversation against each criterion in the rubric. For each criterion:
1. Assign a score based on the scoring guide
2. Cite specific evidence from the conversation (quote or reference specific turns)
3. Provide constructive feedback for improvement

Then provide:
- Overall summary feedback (2-3 paragraphs)
- Top 2-3 strengths
- Top 2-3 areas for improvement
- Your confidence in this evaluation (0.0-1.0)

## Response Format
You MUST respond with valid JSON in exactly this format:
```json
{{
  "criteria_scores": {{
    "<criterion_name>": {{
      "score": <number>,
      "max_score": <number>,
      "evidence": "<specific quotes or observations from the conversation>",
      "feedback": "<constructive feedback for improvement>"
    }}
  }},
  "total_score": <number>,
  "overall_feedback": "<2-3 paragraph summary>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "areas_for_improvement": ["<area 1>", "<area 2>"],
  "confidence": <0.0-1.0>
}}
```

Use the exact criterion names from the rubric (lowercase with underscores).
Respond ONLY with the JSON object, no other text."""

    def _parse_grade_response(self, response: str) -> dict:
        """Parse the grading response from Claude.

        Args:
            response: The raw response text from Claude.

        Returns:
            Parsed grade data dictionary.

        Raises:
            ValueError: If response cannot be parsed.
        """
        # Try to extract JSON from the response
        # Sometimes Claude wraps it in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to parse the whole response as JSON
            json_str = response.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse grading response as JSON: {e}")

        # Validate required fields
        required_fields = [
            'criteria_scores',
            'total_score',
            'overall_feedback',
            'strengths',
            'areas_for_improvement',
            'confidence',
        ]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in grade response: {field}")

        return data

    async def grade_conversation(
        self,
        conversation: Conversation,
        persona: Persona,
    ) -> dict:
        """Grade a completed conversation.

        Args:
            conversation: The conversation to grade.
            persona: The stakeholder persona used in the conversation.

        Returns:
            Dictionary containing grade data ready for storage.

        Raises:
            ValueError: If grading fails.
        """
        if not conversation.messages:
            raise ValueError("Cannot grade conversation with no messages")

        # Build grading prompt
        grading_prompt = self._build_grading_prompt(conversation, persona)

        # Call Claude for grading
        response = await self.llm_client.generate_json_response(
            system_prompt="You are an expert evaluator. Respond only with valid JSON.",
            messages=[{"role": "user", "content": grading_prompt}],
            max_tokens=3000,
        )

        # Parse response
        grade_data = self._parse_grade_response(response)

        return grade_data

    def create_grade_record(
        self,
        conversation_id,
        rubric_id,
        grade_data: dict,
    ) -> Grade:
        """Create a Grade model instance from grade data.

        Args:
            conversation_id: UUID of the graded conversation.
            rubric_id: UUID of the rubric used.
            grade_data: Parsed grade data from Claude.

        Returns:
            Grade model instance (not yet committed to DB).
        """
        return Grade(
            conversation_id=conversation_id,
            rubric_id=rubric_id,
            criteria_scores=grade_data['criteria_scores'],
            total_score=Decimal(str(grade_data['total_score'])),
            overall_feedback=grade_data['overall_feedback'],
            strengths=grade_data['strengths'],
            areas_for_improvement=grade_data['areas_for_improvement'],
            ai_confidence=Decimal(str(grade_data['confidence'])),
            graded_by=GradedBy.AI,
            instructor_override=False,
        )


async def grade_conversation_async(
    conversation: Conversation,
    persona: Persona,
    rubric: Rubric,
) -> Grade:
    """Convenience function to grade a conversation.

    Args:
        conversation: The conversation to grade.
        persona: The stakeholder persona.
        rubric: The grading rubric.

    Returns:
        Grade model instance (not yet committed to DB).
    """
    engine = GradingEngine(rubric)
    grade_data = await engine.grade_conversation(conversation, persona)
    return engine.create_grade_record(
        conversation_id=conversation.id,
        rubric_id=rubric.id,
        grade_data=grade_data,
    )
