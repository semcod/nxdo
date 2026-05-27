"""Tests for ticket_generator module."""

import tempfile
import unittest
from pathlib import Path

from lane.models import Priority, Task, TaskPlan, TaskType
from lane.ticket_generator import (
    TODO_MANAGED_END,
    TODO_MANAGED_START,
    _map_priority,
    _build_todo_section,
    _resolve_todo_path,
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

    def test_sync_to_todo_md_creates_file_with_checkboxes(self) -> None:
        """Test that sync_to_todo_md appends checkboxes to TODO.md."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            generated_at="2026-01-01 12:00 UTC",
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
            report = sync_to_todo_md(task_plan, Path(tmp_dir))

            self.assertIsInstance(report, dict)
            self.assertTrue(report["enabled"])
            self.assertEqual(report["updated"], 1)

            todo_path = Path(report["todo_path"])
            self.assertTrue(todo_path.exists())
            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("- [ ]", content)
            self.assertIn("Test task", content)
            self.assertIn("lane:task-1", content)

    def test_sync_to_todo_md_preserves_existing_content(self) -> None:
        """Test that existing TODO.md content is preserved."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[
                Task(
                    number=1,
                    title="New task",
                    description="",
                    priority=Priority.LOW,
                    task_type=TaskType.CHORE,
                    estimated_hours=None,
                    acceptance_criteria=[],
                    dependencies=[],
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "todo.md"
            todo_path.write_text("# TODO\n\n- [ ] Existing task\n", encoding="utf-8")

            sync_to_todo_md(task_plan, Path(tmp_dir))

            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("Existing task", content)
            self.assertIn("New task", content)

    def test_sync_to_todo_md_is_idempotent(self) -> None:
        """Test that repeated syncs replace the managed block."""
        first_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[
                Task(
                    number=1,
                    title="First generated task",
                    description="",
                    priority=Priority.MEDIUM,
                    task_type=TaskType.CHORE,
                ),
            ],
        )
        second_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            generated_at="2026-01-02 00:00 UTC",
            tasks=[
                Task(
                    number=2,
                    title="Second generated task",
                    description="",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "TODO.md"
            todo_path.write_text("# TODO\n\n- [ ] Manual task\n", encoding="utf-8")

            sync_to_todo_md(first_plan, Path(tmp_dir))
            sync_to_todo_md(second_plan, Path(tmp_dir))

            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("Manual task", content)
            self.assertNotIn("First generated task", content)
            self.assertIn("Second generated task", content)
            self.assertEqual(content.count(TODO_MANAGED_START), 1)
            self.assertEqual(content.count(TODO_MANAGED_END), 1)

    def test_sync_to_todo_md_removes_legacy_generated_sections(self) -> None:
        """Test that old append-only lane sections are replaced."""
        task_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            generated_at="2026-01-03 00:00 UTC",
            tasks=[
                Task(
                    number=3,
                    title="Current generated task",
                    description="",
                    priority=Priority.LOW,
                    task_type=TaskType.CHORE,
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "TODO.md"
            todo_path.write_text(
                "# TODO\n\n"
                "- [ ] Manual before\n\n"
                "## Generated by lane — old\n\n"
                "- [ ] Old generated task  <!-- lane:task-1 -->\n\n"
                "## Manual section\n\n"
                "- [ ] Manual after\n",
                encoding="utf-8",
            )

            sync_to_todo_md(task_plan, Path(tmp_dir))

            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("Manual before", content)
            self.assertIn("Manual section", content)
            self.assertIn("Manual after", content)
            self.assertNotIn("Old generated task", content)
            self.assertIn("Current generated task", content)

    def test_resolve_todo_path_prefers_existing(self) -> None:
        """Test that _resolve_todo_path finds existing todo.md."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "todo.md"
            todo_path.touch()
            result = _resolve_todo_path(Path(tmp_dir))
            self.assertEqual(result, todo_path)

    def test_build_todo_section_contains_checkboxes(self) -> None:
        """Test that _build_todo_section generates correct markdown."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[
                Task(
                    number=3,
                    title="My task",
                    description="My description",
                    priority=Priority.HIGH,
                    task_type=TaskType.BUG,
                    estimated_hours=None,
                    acceptance_criteria=[],
                    dependencies=[],
                ),
            ],
        )
        lines = _build_todo_section(task_plan)
        joined = "\n".join(lines)
        self.assertIn("- [ ]", joined)
        self.assertIn("My task", joined)
        self.assertIn("lane:task-3", joined)
        self.assertIn("Generated by lane", joined)
        self.assertIn(TODO_MANAGED_START, joined)
        self.assertIn(TODO_MANAGED_END, joined)


if __name__ == "__main__":
    unittest.main()
