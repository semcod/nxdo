"""Data models used by nxdo."""

from enum import Enum

from pydantic import BaseModel, Field

from .text_builder import LineBuilder


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
    estimated_hours: float | None = None
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
        task_dict = self.model_dump()
        task_dict["priority"] = self.priority.value
        task_dict["task_type"] = self.task_type.value
        return task_dict


class TaskPlan(BaseModel):
    project_name: str
    summary: str
    tasks: list[Task]
    generated_at: str = ""
    model_used: str = ""

    def __str__(self) -> str:
        builder = LineBuilder(
            f"# Task Plan — {self.project_name}",
            "",
            self.summary,
            "",
            "## Tasks",
            "",
        )
        for task in self.tasks:
            builder.line(str(task))
            builder.line(f"   {task.description}")
            if task.acceptance_criteria:
                builder.line("   Criteria:")
                for criterion in task.acceptance_criteria:
                    builder.line(f"     • {criterion}")
            if task.dependencies:
                deps = ", ".join(str(dep) for dep in task.dependencies)
                builder.line(f"   Dependencies: {deps}")
            builder.line("")
        if self.generated_at:
            builder.line(f"_Generated: {self.generated_at} | Model: {self.model_used}_")
        return builder.text()

    def to_dict(self) -> dict[str, object]:
        return {
            "project_name": self.project_name,
            "summary": self.summary,
            "generated_at": self.generated_at,
            "model_used": self.model_used,
            "tasks": [task.to_dict() for task in self.tasks],
        }

