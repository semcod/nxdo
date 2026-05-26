"""Rich-based rendering helpers for lane output."""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .models import Priority, TaskPlan

_PRIORITY_STYLE = {
    Priority.HIGH: "bold red",
    Priority.MEDIUM: "yellow",
    Priority.LOW: "dim",
}


def render_plan(plan: TaskPlan, console: Console | None = None) -> None:
    """Render a TaskPlan as a Rich table with a summary panel."""
    console = console or Console()

    console.print(
        Panel(
            f"[bold]{plan.project_name}[/bold]\n\n{plan.summary}",
            title="Task Plan",
            subtitle=f"Generated: {plan.generated_at} | Model: {plan.model_used}",
            border_style="blue",
        )
    )

    table = Table(box=box.ROUNDED, show_lines=True, expand=True)
    table.add_column("#", style="dim", width=4, no_wrap=True)
    table.add_column("Type", width=10, no_wrap=True)
    table.add_column("Priority", width=8, no_wrap=True)
    table.add_column("Est.", width=6, no_wrap=True)
    table.add_column("Title")
    table.add_column("Description")

    for task in plan.tasks:
        style = _PRIORITY_STYLE.get(task.priority, "")
        est = f"{task.estimated_hours}h" if task.estimated_hours is not None else "—"
        table.add_row(
            str(task.number),
            task.task_type.value,
            f"[{style}]{task.priority.value}[/{style}]",
            est,
            f"[bold]{task.title}[/bold]",
            task.description,
        )

    console.print(table)


def render_plan_json(plan: TaskPlan, console: Console | None = None) -> None:
    """Print the plan as indented JSON."""
    console = console or Console()
    console.print_json(json.dumps(plan.to_dict(), indent=2))


def render_context(project_text: str, git_text: str, console: Console | None = None) -> None:
    """Render captured project and git context for inspection."""
    console = console or Console()
    console.print(Panel(project_text, title="Project Snapshot", border_style="green"))
    console.print(Panel(git_text, title="Git Context", border_style="cyan"))
