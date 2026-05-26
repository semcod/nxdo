"""Generate task plans with an OpenAI-compatible LLM endpoint."""

from datetime import datetime, timezone
import json
import os
from urllib import error, request

from .models import Priority, Task, TaskPlan, TaskType

DEFAULT_MODEL = os.environ.get("LLM_MODEL", "openrouter/qwen/qwen3-coder-next")
DEFAULT_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")

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


class OpenAICompatibleLLMClient:
    """Minimal client for OpenRouter or another OpenAI-compatible endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        app_name: str = "lane",
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.app_name = app_name

    def generate_task_plan(
        self,
        project_snapshot_text: str,
        git_context_text: str,
        project_name: str,
        extra_context: str = "",
    ) -> TaskPlan:
        raw = self._create_message(
            build_user_prompt(project_snapshot_text, git_context_text, extra_context)
        )
        return parse_task_plan_response(raw, project_name, self.model)

    def _create_message(self, user_message: str) -> str:
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
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:  # pragma: no cover - depends on remote service
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"LLM request failed with HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:  # pragma: no cover - depends on remote service
            raise ValueError(f"LLM request failed: {exc.reason}") from exc

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as exc:
            raise ValueError(f"Unexpected LLM response payload: {data}") from exc


def parse_task_plan_response(raw: str, project_name: str, model: str) -> TaskPlan:
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON. Raw response:\n{raw[:500]}") from exc

    tasks: list[Task] = []
    for item in data.get("tasks", []):
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

    return TaskPlan(
        project_name=data.get("project_name", project_name),
        summary=data.get("summary", ""),
        tasks=tasks,
        generated_at=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        model_used=model,
    )

