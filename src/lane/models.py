"""Data models used by lane."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskType(str, Enum):
    FEATURE = "feature"
    BUG = "bug"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"


class Task(BaseModel):
    number: int
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    task_type: TaskType = TaskType.FEATURE
    estimated_hours: Optional[float] = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    dependencies: list[int] = Field(default_factory=list)

    def __str__(self) -> str:
        tag = f"[{self.task_type.value.upper()}]"
        pri = f"({self.priority.value})"
        est_val = self.estimated_hours
        if est_val is not None:
            est = f" ~{int(est_val) if est_val == int(est_val) else est_val}h"
        else:
            est = ""
        return f"{self.number:02d}. {tag} {pri}{est} {self.title}"

    def to_dict(self) -> dict[str, object]:
        data = self.model_dump()
        data["priority"] = self.priority.value
        data["task_type"] = self.task_type.value
        return data


class TaskPlan(BaseModel):
    project_name: str
    summary: str
    tasks: list[Task]
    generated_at: str = ""
    model_used: str = ""

    def __str__(self) -> str:
        lines = [
            f"# Task Plan — {self.project_name}",
            "",
            self.summary,
            "",
            "## Tasks",
            "",
        ]
        for task in self.tasks:
            lines.append(str(task))
            lines.append(f"   {task.description}")
            if task.acceptance_criteria:
                lines.append("   Criteria:")
                for criterion in task.acceptance_criteria:
                    lines.append(f"     • {criterion}")
            if task.dependencies:
                deps = ", ".join(str(dep) for dep in task.dependencies)
                lines.append(f"   Dependencies: {deps}")
            lines.append("")
        if self.generated_at:
            lines.append(f"_Generated: {self.generated_at} | Model: {self.model_used}_")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, object]:
        return {
            "project_name": self.project_name,
            "summary": self.summary,
            "generated_at": self.generated_at,
            "model_used": self.model_used,
            "tasks": [task.to_dict() for task in self.tasks],
        }

