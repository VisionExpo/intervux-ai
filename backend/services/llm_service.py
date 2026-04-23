import os
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from backend.core.llm_brain import run_safe_json_task
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    Handles high-level LLM interactions, schema validation, and retry logic.
    """

    def __init__(self, default_model: str = "gemini-1.5-flash"):
        self.default_model = os.getenv("LLM_MODEL", default_model)

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """
        Generates a structured response from the LLM, validated against a Pydantic model.
        Uses the 'Verify-then-Trust' pattern with safe JSON parsing.
        """
        # Wrapping the existing logic from llm_brain
        return await run_safe_json_task(
            prompt=prompt,
            response_model=response_model,
            system_instruction=system_instruction,
            temperature=temperature,
        )

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Generates raw text from the LLM.
        """
        # Fallback to a simpler call if needed, but for now we reuse the core brain
        from backend.core.llm_brain import call_llm_raw
        return await call_llm_raw(prompt, system_instruction)
