"""Claude API client wrapper for LLM interactions."""

from typing import Optional
import anthropic

from app.config import get_settings

settings = get_settings()


class LLMClient:
    """Wrapper for Anthropic Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Claude client.

        Args:
            api_key: Anthropic API key. Defaults to settings.anthropic_api_key.
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Add it to your .env file."
            )
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.default_model = "claude-sonnet-4-20250514"

    async def generate_response(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 500,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> str:
        """Generate a response from Claude.

        Args:
            system_prompt: The system prompt defining Claude's role.
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature (0-1).
            model: Model to use. Defaults to claude-sonnet.

        Returns:
            The generated text response.
        """
        response = self.client.messages.create(
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text

    async def generate_json_response(
        self,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 2000,
        model: Optional[str] = None,
    ) -> str:
        """Generate a JSON response from Claude.

        Used for structured outputs like grading.

        Args:
            system_prompt: The system prompt defining Claude's role.
            messages: List of message dicts with 'role' and 'content'.
            max_tokens: Maximum tokens in response.
            model: Model to use.

        Returns:
            The generated JSON string.
        """
        # Lower temperature for more consistent JSON output
        return await self.generate_response(
            system_prompt=system_prompt,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3,
            model=model,
        )


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
