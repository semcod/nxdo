"""Ticket generation integration with planfile."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

from lane.models import Task, TaskPlan

console = Console()


def task_plan_to_tickets(task_plan: TaskPlan) -> list[dict[str, Any]]:
    """Convert TaskPlan to planfile ticket format.

    Args:
        task_plan: TaskPlan from lane planner

    Returns:
        List of ticket dictionaries in planfile format
    """
    tickets: list[dict[str, Any]] = []

    for task in task_plan.tasks:
        ticket = {
            "id": f"task-{task.number}",
            "title": task.title,
            "name": task.title,
            "description": task.description,
            "status": "pending",
            "priority": _map_priority(task.priority.value),
            "task_type": task.task_type.value,
            "estimated_hours": task.estimated_hours,
            "acceptance_criteria": task.acceptance_criteria,
            "dependencies": [f"task-{dep}" for dep in task.dependencies],
        }
        tickets.append(ticket)

    return tickets


def _map_priority(priority: str) -> str:
    """Map lane Priority to planfile priority."""
    priority_map = {
        "high": "critical",
        "medium": "high",
        "low": "medium",
    }
    return priority_map.get(priority.lower(), "medium")


def sync_to_todo_md(task_plan: TaskPlan, project_path: Path = Path(".")) -> dict[str, Any]:
    """Sync TaskPlan tasks to TODO.md as checkboxes.

    This uses planfile's todo_sync functionality to update TODO.md
    with task status from the TaskPlan.

    Args:
        task_plan: TaskPlan from lane planner
        project_path: Project root path

    Returns:
        Sync report dictionary
    """
    try:
        from planfile.todo_sync import sync_todo_checkboxes_from_planfile
    except ImportError:
        console.print("[yellow]⚠️  planfile not available, skipping TODO.md sync[/yellow]")
        return {"enabled": False, "todo_path": "", "updated": 0}

    # Create a temporary strategy file for planfile sync
    strategy_path = project_path / ".lane_strategy.yaml"
    _create_temp_strategy(task_plan, strategy_path)

    try:
        report = sync_todo_checkboxes_from_planfile(
            strategy_path=strategy_path,
            project_path=project_path,
            enabled=True,
        )
        return report
    finally:
        # Clean up temporary strategy file
        if strategy_path.exists():
            strategy_path.unlink()


def _create_temp_strategy(task_plan: TaskPlan, strategy_path: Path) -> None:
    """Create a temporary planfile strategy file for sync.

    Args:
        task_plan: TaskPlan from lane planner
        strategy_path: Path to write strategy file
    """
    import yaml

    strategy_data = {
        "name": task_plan.project_name,
        "description": task_plan.summary,
        "integrations": {
            "markdown": {
                "sync_on_plan_run": True,
                "todo_file": "TODO.md",
            }
        },
        "tasks": [
            {
                "id": f"task-{task.number}",
                "title": task.title,
                "description": task.description,
                "status": "pending",
                "priority": _map_priority(task.priority.value),
            }
            for task in task_plan.tasks
        ],
    }

    with open(strategy_path, "w", encoding="utf-8") as f:
        yaml.dump(strategy_data, f, default_flow_style=False)


def export_to_planfile_yaml(task_plan: TaskPlan, output_path: Path) -> None:
    """Export TaskPlan to planfile YAML format.

    Args:
        task_plan: TaskPlan from lane planner
        output_path: Path to write planfile YAML
    """
    import yaml

    strategy_data = {
        "name": task_plan.project_name,
        "description": task_plan.summary,
        "project_type": "software",
        "domain": "development",
        "goal": task_plan.summary,
        "sprints": [
            {
                "id": 1,
                "name": "Sprint 1",
                "goal": task_plan.summary,
                "task_patterns": [
                    {
                        "id": f"task-{task.number}",
                        "title": task.title,
                        "description": task.description,
                        "status": "pending",
                        "priority": _map_priority(task.priority.value),
                        "task_type": task.task_type.value,
                        "estimated_hours": task.estimated_hours,
                        "acceptance_criteria": task.acceptance_criteria,
                        "dependencies": [f"task-{dep}" for dep in task.dependencies],
                    }
                    for task in task_plan.tasks
                ],
            }
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(strategy_data, f, default_flow_style=False)

    console.print(f"[green]✓ Exported strategy to {output_path}[/green]")
