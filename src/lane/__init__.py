"""lane package."""

from .config import LaneSettings, get_settings
from .git_reader import GitContext, read_git_context
from .llm_client import OpenAICompatibleLLMClient, build_user_prompt, parse_task_plan_response
from .models import Priority, Task, TaskPlan, TaskType
from .planner import generate_next_tasks
from .project_analyzer import ProjectSnapshot, analyze_project
from .providers import LLMProvider, OpenAICompatProvider

__all__ = [
    "GitContext",
    "LLMProvider",
    "LaneSettings",
    "OpenAICompatProvider",
    "OpenAICompatibleLLMClient",
    "Priority",
    "ProjectSnapshot",
    "Task",
    "TaskPlan",
    "TaskType",
    "analyze_project",
    "build_user_prompt",
    "generate_next_tasks",
    "get_settings",
    "parse_task_plan_response",
    "read_git_context",
]

__version__ = "0.2.8"

