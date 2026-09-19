"""Tests for ticket_generator module."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

from nxdo.models import Priority, Task, TaskPlan, TaskType
from nxdo.ticket_generator import (
    TODO_MANAGED_END,
    TODO_MANAGED_START,
    _build_todo_section,
    _map_priority,
    _remove_generated_todo_sections,
    _remove_legacy_generated_todo_sections,
    _remove_managed_todo_blocks,
    _resolve_todo_path,
    _sync_todo_section,
    export_to_planfile_yaml,
    sync_to_planfile,
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
            self.assertIn("nxdo:task-1", content)

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
        """Test that old append-only nxdo sections are replaced."""
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
                "## Generated by nxdo — old\n\n"
                "- [ ] Old generated task  <!-- nxdo:task-1 -->\n\n"
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
        self.assertIn("nxdo:task-3", joined)
        self.assertIn("Generated by nxdo", joined)
        self.assertIn(TODO_MANAGED_START, joined)
        self.assertIn(TODO_MANAGED_END, joined)

    def test_resolve_todo_path_defaults_to_todo_md_when_missing(self) -> None:
        """Test that _resolve_todo_path falls back to TODO.md when none exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = _resolve_todo_path(Path(tmp_dir))
            self.assertEqual(result, Path(tmp_dir) / "TODO.md")

    def test_resolve_todo_path_prefers_uppercase_todo_md(self) -> None:
        """Test that _resolve_todo_path finds an existing TODO.md."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "TODO.md").touch()
            result = _resolve_todo_path(Path(tmp_dir))
            self.assertEqual(result, Path(tmp_dir) / "TODO.md")

    def test_resolve_todo_path_prefers_camelcase_todo_md(self) -> None:
        """Test that _resolve_todo_path finds an existing Todo.md."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "Todo.md").touch()
            result = _resolve_todo_path(Path(tmp_dir))
            self.assertEqual(result, Path(tmp_dir) / "Todo.md")

    def test_resolve_todo_path_prefers_first_candidate(self) -> None:
        """Test that TODO.md wins over todo.md when both exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "TODO.md").touch()
            (Path(tmp_dir) / "todo.md").touch()
            result = _resolve_todo_path(Path(tmp_dir))
            self.assertEqual(result, Path(tmp_dir) / "TODO.md")

    def test_map_priority_is_case_insensitive(self) -> None:
        """Test that _map_priority is case-insensitive."""
        self.assertEqual(_map_priority("HIGH"), "critical")
        self.assertEqual(_map_priority("High"), "critical")
        self.assertEqual(_map_priority("MEDIUM"), "high")
        self.assertEqual(_map_priority("LOW"), "medium")

    def test_sync_to_todo_md_empty_plan_writes_markers_only(self) -> None:
        """Test that an empty plan still writes the managed block markers."""
        task_plan = TaskPlan(project_name="proj", summary="sum", tasks=[])

        with tempfile.TemporaryDirectory() as tmp_dir:
            report = sync_to_todo_md(task_plan, Path(tmp_dir))

            self.assertTrue(report["enabled"])
            self.assertEqual(report["updated"], 0)
            content = (Path(tmp_dir) / "TODO.md").read_text(encoding="utf-8")
            self.assertIn(TODO_MANAGED_START, content)
            self.assertIn(TODO_MANAGED_END, content)
            self.assertNotIn("- [ ]", content)

    def test_sync_to_todo_md_multiple_tasks(self) -> None:
        """Test that multiple tasks all appear as checkboxes."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[
                Task(
                    number=1,
                    title="First",
                    description="",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                ),
                Task(
                    number=2,
                    title="Second",
                    description="",
                    priority=Priority.LOW,
                    task_type=TaskType.BUG,
                ),
            ],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            report = sync_to_todo_md(task_plan, Path(tmp_dir))

            self.assertEqual(report["updated"], 2)
            content = (Path(tmp_dir) / "TODO.md").read_text(encoding="utf-8")
            self.assertIn("nxdo:task-1", content)
            self.assertIn("nxdo:task-2", content)
            self.assertIn("First", content)
            self.assertIn("Second", content)
            self.assertEqual(content.count("- [ ]"), 2)

    def test_sync_to_todo_md_report_shape(self) -> None:
        """Test that sync_to_todo_md returns a complete report dict."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            tasks=[Task(number=1, title="T", description="", priority=Priority.LOW, task_type=TaskType.CHORE)],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            report = sync_to_todo_md(task_plan, Path(tmp_dir))

            self.assertEqual(report["enabled"], True)
            self.assertEqual(report["todo_path"], str(Path(tmp_dir) / "TODO.md"))
            self.assertEqual(report["updated"], 1)

    def test_sync_to_todo_md_handles_file_without_trailing_newline(self) -> None:
        """Test sync when the existing TODO.md lacks a trailing newline."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[Task(number=1, title="New", description="", priority=Priority.MEDIUM, task_type=TaskType.CHORE)],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "TODO.md"
            todo_path.write_text("# TODO\n- [ ] Manual", encoding="utf-8")

            sync_to_todo_md(task_plan, Path(tmp_dir))

            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("- [ ] Manual", content)
            self.assertIn("New", content)

    def test_build_todo_section_priority_emojis(self) -> None:
        """Test that each priority maps to the expected emoji."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[
                Task(number=1, title="High task", description="", priority=Priority.HIGH, task_type=TaskType.FEATURE),
                Task(number=2, title="Med task", description="", priority=Priority.MEDIUM, task_type=TaskType.FEATURE),
                Task(number=3, title="Low task", description="", priority=Priority.LOW, task_type=TaskType.FEATURE),
            ],
        )

        lines = _build_todo_section(task_plan)
        joined = "\n".join(lines)

        self.assertIn("🔴 High task", joined)
        self.assertIn("🟠 Med task", joined)
        self.assertIn("🟡 Low task", joined)

    def test_build_todo_section_defaults_to_latest_when_generated_at_empty(self) -> None:
        """Test that an empty generated_at renders as 'latest'."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            tasks=[Task(number=1, title="T", description="", priority=Priority.LOW, task_type=TaskType.CHORE)],
        )

        lines = _build_todo_section(task_plan)
        joined = "\n".join(lines)

        self.assertIn("## Generated by nxdo — latest", joined)

    def test_build_todo_section_omits_empty_description(self) -> None:
        """Test that tasks without a description do not emit a blank line."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[Task(number=1, title="No desc", description="", priority=Priority.LOW, task_type=TaskType.CHORE)],
        )

        lines = _build_todo_section(task_plan)

        self.assertIn("- [ ] 🟡 No desc  <!-- nxdo:task-1 -->", lines)
        self.assertNotIn("  ", lines)

    def test_remove_managed_todo_blocks_no_markers_returns_unchanged(self) -> None:
        """Test that content without markers is returned unchanged."""
        lines = ["# TODO", "", "- [ ] Manual task"]
        result = _remove_managed_todo_blocks(lines)
        self.assertEqual(result, lines)

    def test_remove_managed_todo_blocks_preserves_content_around_block(self) -> None:
        """Test that content before and after a managed block is preserved."""
        lines = [
            "# TODO",
            "- [ ] Before",
            TODO_MANAGED_START,
            "- [ ] Generated",
            TODO_MANAGED_END,
            "- [ ] After",
        ]
        result = _remove_managed_todo_blocks(lines)
        self.assertEqual(result, ["# TODO", "- [ ] Before", "- [ ] After"])

    def test_remove_managed_todo_blocks_unterminated_block_drops_tail(self) -> None:
        """Test that an unterminated managed block drops everything after it."""
        lines = ["# TODO", TODO_MANAGED_START, "- [ ] Generated", "- [ ] Tail"]
        result = _remove_managed_todo_blocks(lines)
        self.assertEqual(result, ["# TODO"])

    def test_remove_legacy_generated_todo_sections_removes_until_next_heading(self) -> None:
        """Test that a legacy nxdo section is removed up to the next heading."""
        lines = [
            "# TODO",
            "## Generated by nxdo — old",
            "- [ ] Old task",
            "## Manual section",
            "- [ ] Manual task",
        ]
        result = _remove_legacy_generated_todo_sections(lines)
        self.assertEqual(result, ["# TODO", "## Manual section", "- [ ] Manual task"])

    def test_remove_legacy_generated_todo_sections_without_heading_unchanged(self) -> None:
        """Test that content without a legacy heading is unchanged."""
        lines = ["# TODO", "## Manual section", "- [ ] Manual task"]
        result = _remove_legacy_generated_todo_sections(lines)
        self.assertEqual(result, lines)

    def test_remove_generated_todo_sections_strips_both_kinds(self) -> None:
        """Test that managed and legacy sections are both removed."""
        content = (
            "# TODO\n"
            "- [ ] Manual\n"
            f"{TODO_MANAGED_START}\n"
            "- [ ] Managed\n"
            f"{TODO_MANAGED_END}\n"
            "## Generated by nxdo — old\n"
            "- [ ] Legacy\n"
        )
        result = _remove_generated_todo_sections(content)
        self.assertIn("- [ ] Manual", result)
        self.assertNotIn("Managed", result)
        self.assertNotIn("Legacy", result)

    def test_sync_todo_section_creates_file_with_default_header(self) -> None:
        """Test that _sync_todo_section creates a missing file with the default header."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            todo_path = Path(tmp_dir) / "TODO.md"
            _sync_todo_section(todo_path, ["", TODO_MANAGED_START, "- [ ] T", TODO_MANAGED_END, ""])

            content = todo_path.read_text(encoding="utf-8")
            self.assertIn("# TODO", content)
            self.assertIn("- [ ] T", content)

    def test_task_plan_to_tickets_empty_plan(self) -> None:
        """Test that an empty plan produces no tickets."""
        task_plan = TaskPlan(project_name="proj", summary="sum", tasks=[])
        self.assertEqual(task_plan_to_tickets(task_plan), [])

    def test_task_plan_to_tickets_dependency_mapping(self) -> None:
        """Test that dependencies are mapped to task-N ids."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            tasks=[
                Task(
                    number=2,
                    title="Dep task",
                    description="",
                    priority=Priority.MEDIUM,
                    task_type=TaskType.FEATURE,
                    dependencies=[1],
                ),
            ],
        )
        tickets = task_plan_to_tickets(task_plan)
        self.assertEqual(tickets[0]["dependencies"], ["task-1"])

    def test_sync_to_planfile_when_not_installed(self) -> None:
        """Test sync_to_planfile returns disabled report when install check fails."""
        task_plan = TaskPlan(project_name="proj", summary="sum", tasks=[])
        with patch("nxdo.ticket_generator._ensure_planfile_installed", return_value=False):
            report = sync_to_planfile(task_plan)
            self.assertFalse(report["enabled"])
            self.assertEqual(report["created"], 0)

    def test_sync_to_planfile_success_and_error_handling(self) -> None:
        """Test sync_to_planfile creates tickets and calls sync_integration."""
        task_plan = TaskPlan(
            project_name="proj",
            summary="sum",
            tasks=[
                Task(number=1, title="T1", description="D1", priority=Priority.HIGH, task_type=TaskType.FEATURE),
                Task(number=2, title="T2", description="D2", priority=Priority.LOW, task_type=TaskType.BUG),
            ],
        )

        mock_store_inst = MagicMock()
        mock_store_inst.base_dir = Path("/tmp/.planfile")
        mock_store_cls = MagicMock(return_value=mock_store_inst)
        # Make second ticket fail to test exception handling
        mock_store_inst.create_ticket.side_effect = [None, ValueError("duplicate")]

        mock_sync_integration = MagicMock()

        # Build mock planfile modules
        mock_core = ModuleType("planfile.core")
        mock_store_mod = ModuleType("planfile.core.store")
        mock_store_mod.Store = mock_store_cls
        mock_models = ModuleType("planfile.core.models")
        mock_models.Ticket = MagicMock()
        mock_models.TicketStatus = MagicMock()
        mock_cli_sync = ModuleType("planfile.cli.groups.sync.core")
        mock_cli_sync.sync_integration = mock_sync_integration

        mock_modules = {
            "planfile.core": mock_core,
            "planfile.core.store": mock_store_mod,
            "planfile.core.models": mock_models,
            "planfile.cli.groups.sync.core": mock_cli_sync,
        }

        with (
            patch("nxdo.ticket_generator._ensure_planfile_installed", return_value=True),
            patch.dict(sys.modules, mock_modules),
        ):
            report = sync_to_planfile(task_plan)
            self.assertTrue(report["enabled"])
            self.assertEqual(report["created"], 1)
            self.assertEqual(report["planfile_dir"], "/tmp/.planfile")


if __name__ == "__main__":
    unittest.main()
