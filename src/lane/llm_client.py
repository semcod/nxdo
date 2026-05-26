"""Generate task plans with an OpenAI-compatible LLM endpoint.

This module is kept for backwards compatibility. New code should use
``lane.providers.OpenAICompatProvider`` and ``lane.planner.generate_next_tasks``.
"""

from __future__ import annotations

import os

from .models import TaskPlan
from .providers.openai_compat import OpenAICompatProvider, _parse_response

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "openrouter/qwen/qwen3-coder-next")
DEFAULT_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")

USER_PROMPT_TEMPLATE = """\
Analyze the following project and generate the next 10 tasks.

=== PROJECT STATE ===
{project_snapshot}

=== GIT HISTORY ===
{git_context}

=== ADDITIONAL CONTEXT ===
{extra_context}

Generate the task plan now.
"""


def build_user_prompt(project_snapshot_text: str, git_context_text: str, extra_context: str = "") -> str:
    return USER_PROMPT_TEMPLATE.format(
        project_snapshot=project_snapshot_text,
        git_context=git_context_text,
        extra_context=extra_context or "None provided.",
    )


def parse_task_plan_response(raw: str, project_name: str, model: str) -> TaskPlan:
    """Parse a raw JSON string from the LLM into a TaskPlan. (Compatibility wrapper.)"""
    return _parse_response(raw, project_name, model)


class OpenAICompatibleLLMClient:
    """Minimal client for OpenRouter or another OpenAI-compatible endpoint.

    Kept for backwards compatibility; delegates to OpenAICompatProvider.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        app_name: str = "lane",
    ) -> None:
        self._provider = OpenAICompatProvider(
            api_key=api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY"),
            model=model,
            base_url=base_url,
            app_name=app_name,
        )
        self.api_key = self._provider.api_key
        self.model = self._provider.model
        self.base_url = self._provider.base_url

    def generate_task_plan(
        self,
        project_snapshot_text: str,
        git_context_text: str,
        project_name: str,
        extra_context: str = "",
    ) -> TaskPlan:
        user_prompt = build_user_prompt(project_snapshot_text, git_context_text, extra_context)
        return self._provider.generate_plan(user_prompt, project_name)
