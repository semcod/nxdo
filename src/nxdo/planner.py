"""Central orchestrator: compose project + git + prompt + LLM into a TaskPlan."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import NxdoSettings, get_settings
from .git_reader import read_git_context
from .llm_client import build_user_prompt
from .models import TaskPlan
from .project_analyzer import analyze_project
from .providers import LLMProvider, OpenAICompatProvider


def generate_next_tasks(
    repo_path: Path,
    extra_context: str = "",
    provider: Optional[LLMProvider] = None,
    settings: Optional[NxdoSettings] = None,
    koru_aware: bool = False,
) -> TaskPlan:
    """Analyze *repo_path* and return a TaskPlan with the next 10 tasks.

    Args:
        repo_path: Path to the git repository to analyze.
        extra_context: Optional additional guidance to include in the prompt.
        provider: An LLMProvider instance. Defaults to OpenAICompatProvider.
        settings: Configuration override; uses environment defaults if omitted.
        koru_aware: If True, load koru integration schema and include in prompt.

    Returns:
        A validated TaskPlan containing up to 10 prioritized tasks.
    """
    cfg = settings or get_settings()

    snapshot = analyze_project(repo_path)
    git_context = read_git_context(repo_path, max_commits=cfg.max_commits)

    # Build koru context if requested
    koru_schema = ""
    if koru_aware:
        from .koru_context import build_koru_context
        koru_ctx = build_koru_context(repo_path, include_project_state=True)
        if koru_ctx.available:
            koru_schema = koru_ctx.schema_text

    user_prompt = build_user_prompt(
        snapshot.to_text(),
        git_context.to_text(),
        extra_context,
        koru_schema=koru_schema,
    )

    if provider is None:
        provider = OpenAICompatProvider(settings=cfg, koru_aware=koru_aware)

    return provider.generate_plan(user_prompt, project_name=snapshot.name)
