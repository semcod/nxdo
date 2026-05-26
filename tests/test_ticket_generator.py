"""Tests for ticket_generator module."""

import tempfile
import unittest
from pathlib import Path

from lane.models import Priority, Task, TaskPlan, TaskType
from lane.ticket_generator import (
    _map_priority,
    export_to_planfile_yaml,
    sync_to_todo_md,
    task_plan_to_tickets,
)


class TicketGeneratorTests(unittest.TestCase):
    def test_task_plan_to_tickets(self) -> None:
        """Test converting TaskPlan to planfile ticket format."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[
                Task(
                    number=1,
                    title="First task",
                    description="Description of first task",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                    estimated_hours=2.5,
                    acceptance_criteria=["criteria 1", "criteria 2"],
                    dependencies=[],
                ),
                Task(
                    number=2,
                    title="Second task",
                    description="Description of second task",
                    priority=Priority.LOW,
                    task_type=TaskType.BUG,
                    estimated_hours=1.0,
                    acceptance_criteria=["criteria 3"],
                    dependencies=[1],
                ),
            ],
        )

        tickets = task_plan_to_tickets(task_plan)

        self.assertEqual(len(tickets), 2)
        self.assertEqual(tickets[0]["id"], "task-1")
        self.assertEqual(tickets[0]["title"], "First task")
        self.assertEqual(tickets[0]["priority"], "critical")
        self.assertEqual(tickets[0]["task_type"], "feature")
        self.assertEqual(tickets[1]["id"], "task-2")
        self.assertEqual(tickets[1]["dependencies"], ["task-1"])

    def test_map_priority(self) -> None:
        """Test priority mapping."""
        self.assertEqual(_map_priority("high"), "critical")
        self.assertEqual(_map_priority("medium"), "high")
        self.assertEqual(_map_priority("low"), "medium")
        self.assertEqual(_map_priority("unknown"), "medium")

    def test_export_to_planfile_yaml(self) -> None:
        """Test exporting TaskPlan to planfile YAML format."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[
                Task(
                    number=1,
                    title="Test task",
                    description="Test description",
                    priority=Priority.MEDIUM,
                    task_type=TaskType.FEATURE,
                    estimated_hours=1.0,
                    acceptance_criteria=["criteria"],
                    dependencies=[],
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "strategy.yaml"
            export_to_planfile_yaml(task_plan, output_path)

            self.assertTrue(output_path.exists())

            # Verify YAML content
            import yaml

            with open(output_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            self.assertEqual(data["name"], "test-project")
            self.assertEqual(data["description"], "Test summary")
            self.assertEqual(len(data["sprints"]), 1)
            self.assertEqual(len(data["sprints"][0]["task_patterns"]), 1)
            self.assertEqual(data["sprints"][0]["task_patterns"][0]["title"], "Test task")

    def test_sync_to_todo_md_without_planfile(self) -> None:
        """Test syncing to TODO.md when planfile is not available."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[
                Task(
                    number=1,
                    title="Test task",
                    description="Test description",
                    priority=Priority.MEDIUM,
                    task_type=TaskType.FEATURE,
                    estimated_hours=1.0,
                    acceptance_criteria=["criteria"],
                    dependencies=[],
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            # This should not raise an error even if planfile is not available
            report = sync_to_todo_md(task_plan, Path(tmp_dir))
            self.assertIsInstance(report, dict)
            self.assertIn("enabled", report)


if __name__ == "__main__":
    unittest.main()
