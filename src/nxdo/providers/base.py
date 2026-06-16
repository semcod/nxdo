"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import TaskPlan


class LLMProvider(ABC):
    """Interface every LLM backend must implement."""

    @abstractmethod
    def generate_plan(
        self,
        user_prompt: str,
        project_name: str,
    ) -> TaskPlan:
        """Send *user_prompt* to the model and return a validated TaskPlan."""
