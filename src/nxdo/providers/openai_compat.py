"""OpenAI-compatible LLM provider using httpx and tenacity for reliability."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..config import NxdoSettings, get_settings
from ..models import Priority, Task, TaskPlan, TaskType
from .base import LLMProvider

SYSTEM_PROMPT = """\
You are an expert software engineering project manager and technical lead.
Your role is to analyze a software project's current state and recent development
history, then produce a concrete, prioritized plan of the next 10 tasks.

RULES:
- Tasks must be specific and actionable with detailed descriptions (2-4 sentences).
- Each task should fit in a focused work session of roughly 1-8 hours.
- Use the current project state, recent git changes and the user's extra context.
- Mix features, bug fixes, refactoring, tests and docs when appropriate.
- Respond ONLY with valid JSON.
- NEVER use empty strings for description or acceptance_criteria.

DESCRIPTION REQUIREMENTS:
- Minimum 2 sentences explaining WHAT the task does and WHY it matters
- Include specific files, functions, or components when known
- Mention the expected outcome or benefit

ACCEPTANCE CRITERIA REQUIREMENTS:
- Provide 2-4 concrete, verifiable criteria per task
- Must be testable outcomes (e.g., "All tests pass", "Code coverage > 80%")

JSON schema:
{
  "project_name": "string",
  "summary": "2-3 sentence analysis of project state and priorities",
  "tasks": [
    {
      "number": 1,
      "title": "short imperative title (max 5 words)",
      "description": "2-4 sentences: what to do, why it matters, expected outcome",
      "priority": "high|medium|low",
      "task_type": "feature|bug|refactor|docs|test|chore",
      "estimated_hours": 2.0,
      "acceptance_criteria": ["criterion 1", "criterion 2", "criterion 3"],
      "dependencies": []
    }
  ]
}
"""


class LLMAPIError(ValueError):
    """An LLM API failure with structured, actionable detail.

    Subclasses :class:`ValueError` so existing callers that catch ``ValueError``
    (e.g. the CLI) keep working unchanged while gaining access to the extra
    context attributes.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        endpoint: str = "",
        model: str | None = None,
        response_body: str = "",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
        self.model = model
        self.response_body = response_body


_HTTP_STATUS_HINTS = {
    400: "the request payload was rejected; verify your parameters",
    401: "your API key is missing or invalid; check OPENROUTER_API_KEY/OPENAI_API_KEY",
    402: "your account has insufficient credits",
    403: "your API key does not have access to this model or endpoint",
    404: "the model or endpoint was not found; verify the model name",
    408: "the request timed out; retry",
    409: "the request conflicted with another in-flight request",
    413: "the request was too large; reduce the prompt size",
    422: "the request failed validation; check your payload",
    429: "you are rate limited or out of credits; wait and retry",
    500: "the provider returned an internal server error; retry later",
    502: "the provider gateway returned a bad gateway; retry later",
    503: "the provider is temporarily unavailable; retry later",
    504: "the provider gateway timed out; retry later",
}


def _extract_error_detail(response_body: str) -> str:
    """Extract a human-readable message from an API error body.

    Supports the OpenAI/OpenRouter error envelope
    (``{"error": {"message": ...}}``) and simple ``{"message": ...}`` bodies,
    falling back to the raw (truncated) text.
    """
    body = (response_body or "").strip()
    if not body:
        return ""
    try:
        error_json = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return body[:500]
    if isinstance(error_json, dict):
        error = error_json.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
        if isinstance(error, str) and error.strip():
            return error.strip()
        message = error_json.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return body[:500]


def _http_status_hint(status_code: int) -> str:
    """Return an actionable hint for a given HTTP status code."""
    return _HTTP_STATUS_HINTS.get(status_code, "check the provider status and retry")


class OpenAICompatProvider(LLMProvider):
    """Provider for OpenRouter or any OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        settings: NxdoSettings | None = None,
        app_name: str = "nxdo",
        koru_aware: bool = False,
    ) -> None:
        settings = settings or get_settings()
        self.api_key = api_key or settings.api_key
        self.model = model or settings.llm_model
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.timeout = settings.llm_timeout
        self.max_retries = settings.llm_max_retries
        self.app_name = app_name
        self.koru_aware = koru_aware

    def generate_plan(self, user_prompt: str, project_name: str) -> TaskPlan:
        raw = self._call_api(user_prompt)
        return _parse_response(ResponseInputs(raw=raw, project_name=project_name, model=self.model))

    @retry(
        retry=retry_if_exception_type(httpx.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _call_api(self, user_message: str) -> str:
        if not self.api_key:
            raise LLMAPIError(
                "Missing API key. Set OPENROUTER_API_KEY or OPENAI_API_KEY before generating a task plan."
            )

        # Build system prompt with koru extension if enabled
        system_prompt = SYSTEM_PROMPT
        if self.koru_aware:
            from ..koru_context import get_koru_system_prompt_extension
            system_prompt += get_koru_system_prompt_extension()

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv(
                "OPENROUTER_APP_URL", "https://github.com/semcod/nxdo"
            ),
            "X-OpenRouter-Title": os.getenv("OPENROUTER_APP_NAME", self.app_name),
        }

        endpoint = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                endpoint,
                json=payload,
                headers=headers,
            )

        if not response.is_success:
            detail = _extract_error_detail(response.text)
            hint = _http_status_hint(response.status_code)
            message = f"LLM API request failed with HTTP {response.status_code}"
            if detail:
                message += f": {detail}"
            message += f". Hint: {hint}."
            if endpoint:
                message += f" Endpoint: {endpoint}."
            if self.model:
                message += f" Model: {self.model}."
            raise LLMAPIError(
                message,
                status_code=response.status_code,
                endpoint=endpoint,
                model=self.model,
                response_body=(response.text or "")[:1000],
            )

        try:
            response_json = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise LLMAPIError(
                f"LLM API returned a non-JSON success response: {exc}",
                status_code=response.status_code,
                endpoint=endpoint,
                model=self.model,
                response_body=(response.text or "")[:1000],
            ) from exc

        try:
            return response_json["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError, TypeError) as exc:
            raise LLMAPIError(
                f"Unexpected LLM response payload (missing {exc}). Received: {response_json}",
                model=self.model,
            ) from exc


@dataclass
class ResponseInputs:
    """Raw LLM response text plus the metadata needed to parse it into a TaskPlan."""

    raw: str
    project_name: str
    model: str


def _strip_markdown_fences(raw: str) -> str:
    """Remove markdown code fences from the response."""
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()
    return raw


def _parse_json_response(raw: str) -> dict:
    """Parse JSON from raw response with error handling."""
    try:
        parsed_json = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON. Raw response:\n{raw[:500]}") from exc

    if not isinstance(parsed_json, dict):
        # ValueError is the documented parse-error contract consumed by the CLI
        # error handler and the public parse_task_plan_response API.
        raise ValueError(f"Expected a JSON object, got: {type(parsed_json).__name__}")  # noqa: TRY004

    return parsed_json


def _create_task_from_dict(item: dict, task_index: int) -> Task:
    """Create a Task object from a dictionary item."""
    try:
        # Handle dependencies - convert to list of ints, filtering out non-int values
        raw_deps = item.get("dependencies", [])
        dependencies = []
        for dep in raw_deps:
            if isinstance(dep, int):
                dependencies.append(dep)
            elif isinstance(dep, str) and dep.isdigit():
                dependencies.append(int(dep))
            # Skip non-integer dependencies (e.g., task titles)

        return Task(
            number=int(item.get("number", task_index + 1)),
            title=item.get("title", "Untitled task"),
            description=item.get("description", ""),
            priority=Priority(item.get("priority", Priority.MEDIUM.value)),
            task_type=TaskType(item.get("task_type", TaskType.FEATURE.value)),
            estimated_hours=item.get("estimated_hours"),
            acceptance_criteria=list(item.get("acceptance_criteria", [])),
            dependencies=dependencies,
        )
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid task data in LLM response: {item}") from exc


def _parse_tasks_from_data(plan_json: dict) -> list[Task]:
    """Parse tasks from the parsed plan JSON."""
    tasks: list[Task] = []
    for index, item in enumerate(plan_json.get("tasks", [])):
        tasks.append(_create_task_from_dict(item, index))
    return tasks


def _parse_response(inputs: ResponseInputs) -> TaskPlan:
    """Parse and validate the raw JSON response from the LLM."""
    raw = _strip_markdown_fences(inputs.raw)
    plan_json = _parse_json_response(raw)
    tasks = _parse_tasks_from_data(plan_json)

    return TaskPlan(
        project_name=plan_json.get("project_name", inputs.project_name),
        summary=plan_json.get("summary", ""),
        tasks=tasks,
        generated_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        model_used=inputs.model,
    )
