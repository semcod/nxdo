"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..models import TaskPlan


@dataclass
class PlanRequest:
    """User prompt plus project identity forwarded together to the LLM backend."""

    user_prompt: str
    project_name: str


class LLMProvider(ABC):
    """Interface every LLM backend must implement."""

    @abstractmethod
    def generate_plan(self, request: PlanRequest) -> TaskPlan:
        """Send the request's user prompt to the model and return a validated TaskPlan."""
