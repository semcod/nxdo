"""OpenAI-compatible LLM provider using httpx and tenacity for reliability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import LaneSettings, get_settings
from ..models import Priority, Task, TaskPlan, TaskType
from .base import LLMProvider

SYSTEM_PROMPT = """\
You are an expert software engineering project manager and technical lead.
Your role is to analyze a software project's current state and recent development
history, then produce a concrete, prioritized plan of the next 10 tasks.

RULES:
- Tasks must be specific and actionable.
- Each task should fit in a focused work session of roughly 1-8 hours.
- Use the current project state, recent git changes and the user's extra context.
- Mix features, bug fixes, refactoring, tests and docs when appropriate.
- Respond ONLY with valid JSON.

JSON schema:
{
  "project_name": "string",
  "summary": "2-3 sentence analysis",
  "tasks": [
    {
      "number": 1,
      "title": "short imperative title",
      "description": "1-2 sentence description",
      "priority": "high|medium|low",
      "task_type": "feature|bug|refactor|docs|test|chore",
      "estimated_hours": 2.0,
      "acceptance_criteria": ["criterion 1"],
      "dependencies": []
    }
  ]
}
"""


class OpenAICompatProvider(LLMProvider):
    """Provider for OpenRouter or any OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        settings: Optional[LaneSettings] = None,
        app_name: str = "lane",
    ) -> None:
        cfg = settings or get_settings()
        self.api_key = api_key or cfg.api_key
        self.model = model or cfg.llm_model
        self.base_url = (base_url or cfg.llm_base_url).rstrip("/")
        self.timeout = cfg.llm_timeout
        self.max_retries = cfg.llm_max_retries
        self.app_name = app_name

    def generate_plan(self, user_prompt: str, project_name: str) -> TaskPlan:
        raw = self._call_api(user_prompt)
        return _parse_response(raw, project_name, self.model)

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _call_api(self, user_message: str) -> str:
        if not self.api_key:
            raise ValueError(
                "Missing API key. Set OPENROUTER_API_KEY or OPENAI_API_KEY before generating a task plan."
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/semcod/lane",
            "X-Title": self.app_name,
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise ValueError(f"Unexpected LLM response payload: {data}") from exc


def _parse_response(raw: str, project_name: str, model: str) -> TaskPlan:
    """Parse and validate the raw JSON response from the LLM."""
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON. Raw response:\n{raw[:500]}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got: {type(data).__name__}")

    tasks: list[Task] = []
    for item in data.get("tasks", []):
        try:
            tasks.append(
                Task(
                    number=int(item.get("number", len(tasks) + 1)),
                    title=item.get("title", "Untitled task"),
                    description=item.get("description", ""),
                    priority=Priority(item.get("priority", Priority.MEDIUM.value)),
                    task_type=TaskType(item.get("task_type", TaskType.FEATURE.value)),
                    estimated_hours=item.get("estimated_hours"),
                    acceptance_criteria=list(item.get("acceptance_criteria", [])),
                    dependencies=list(item.get("dependencies", [])),
                )
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid task data in LLM response: {item}") from exc

    return TaskPlan(
        project_name=data.get("project_name", project_name),
        summary=data.get("summary", ""),
        tasks=tasks,
        generated_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        model_used=model,
    )
