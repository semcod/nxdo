from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from nxdo.cli import app, app_entry, main
from typer.testing import CliRunner

runner = CliRunner()


class CLITests(unittest.TestCase):
    def test_print_prompt_mode_outputs_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# demo\n\nDemo repository\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root), "--print-prompt", "--max-commits", "1"])

        self.assertEqual(exit_code, 0)
        self.assertIn("=== PROJECT STATE ===", stdout.getvalue())

    def test_print_prompt_includes_extra_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root), "--print-prompt", "--extra-context", "special question"])

        self.assertEqual(exit_code, 0)
        self.assertIn("special question", stdout.getvalue())

    def test_missing_api_key_returns_exit_1(self) -> None:
        from nxdo.config import NxdoSettings

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            import os

            env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                with patch("nxdo.cli.get_settings", return_value=NxdoSettings(_env_file=None)):
                    exit_code = main([str(root)])

        self.assertEqual(exit_code, 1)

    def test_print_context_raw_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                main([str(root), "--print-prompt", "--max-commits", "1"])
                output = stdout.getvalue()
                self.assertIn("Project:", output)

    def test_json_mode_outputs_json(self) -> None:
        from nxdo.config import NxdoSettings

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            import os

            env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                with patch("nxdo.cli.get_settings", return_value=NxdoSettings(_env_file=None)):
                    exit_code = main([str(root), "--json"])
                    self.assertEqual(exit_code, 1)  # No API key, so fails

    def test_max_commits_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO):
                exit_code = main([str(root), "--print-prompt", "--max-commits", "5"])
                self.assertEqual(exit_code, 0)

    def test_app_entry_exists(self) -> None:
        self.assertTrue(callable(app_entry))

    def test_typer_print_context_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["print-context", str(root), "--raw"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Project:", result.stdout)

    def test_typer_print_context_rich_render(self) -> None:
        """Test print-context without --raw to cover render_context branch (line 80)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["print-context", str(root)])
            self.assertEqual(result.exit_code, 0)

    @patch("nxdo.cli.generate_next_tasks")
    def test_plan_command_max_commits_branch(self, mock_generate: MagicMock) -> None:
        """Test that --max-commits overrides cfg.max_commits (line 43)."""
        from nxdo.models import TaskPlan
        mock_plan = TaskPlan(project_name="p", summary="s", tasks=[])
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["plan", str(root), "--max-commits", "5"])
            self.assertEqual(result.exit_code, 0)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_generates_and_displays(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets happy path (lines 125-163)."""
        from nxdo.models import TaskPlan, Task, Priority, TaskType
        mock_plan = TaskPlan(
            project_name="test",
            summary="test summary",
            generated_at="2026-01-01 00:00 UTC",
            tasks=[
                Task(
                    number=1,
                    title="Do something",
                    description="Details",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                )
            ],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root)])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Generated 1 tickets", result.stdout)
            self.assertIn("Do something", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_sync_todo(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets with --sync-todo flag."""
        from nxdo.models import TaskPlan, Task, Priority, TaskType
        mock_plan = TaskPlan(
            project_name="test", summary="s", generated_at="2026-01-01 00:00 UTC",
            tasks=[Task(number=1, title="T", description="", priority=Priority.LOW, task_type=TaskType.CHORE)],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root), "--sync-todo"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Synced 1 tasks", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_export_yaml(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets with --export-yaml flag."""
        from nxdo.models import TaskPlan, Task, Priority, TaskType
        mock_plan = TaskPlan(
            project_name="test", summary="s", generated_at="2026-01-01 00:00 UTC",
            tasks=[Task(number=1, title="T", description="", priority=Priority.LOW, task_type=TaskType.CHORE)],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root), "--export-yaml"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Exported strategy", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_max_commits_branch(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets --max-commits override (line 127)."""
        from nxdo.models import TaskPlan
        mock_plan = TaskPlan(project_name="p", summary="s", generated_at="2026-01-01 00:00 UTC", tasks=[])
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root), "--max-commits", "5"])
            self.assertEqual(result.exit_code, 0)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_sync_planfile(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets with --sync-planfile flag."""
        from nxdo.models import TaskPlan, Task, Priority, TaskType
        mock_plan = TaskPlan(
            project_name="test", summary="s", generated_at="2026-01-01 00:00 UTC",
            tasks=[Task(number=1, title="T", description="", priority=Priority.HIGH, task_type=TaskType.FEATURE)],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root), "--sync-planfile"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Generated 1 tickets", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_tickets_value_error(self, mock_generate: MagicMock) -> None:
        """Test cmd_tickets handles ValueError."""
        mock_generate.side_effect = ValueError("Missing API key")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = runner.invoke(app, ["tickets", str(root)])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error", result.stderr or result.output)

    def test_typer_print_prompt_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["print-prompt", str(root)])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("=== PROJECT STATE ===", result.stdout)

    def test_typer_validate_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            plan_file = Path(tmp_dir) / "plan.json"
            plan_file.write_text(
                '{"project_name": "test", "summary": "test", "tasks": [], "generated_at": "", "model_used": ""}',
                encoding="utf-8",
            )
            result = runner.invoke(app, ["validate", str(plan_file)])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("valid", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_typer_plan_command_with_mocked_provider(self, mock_generate: MagicMock) -> None:
        from nxdo.models import TaskPlan, Task, Priority, TaskType

        mock_plan = TaskPlan(
            project_name="test-project",
            summary="Test plan",
            tasks=[
                Task(
                    number=1,
                    title="Test task",
                    description="Test description",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                )
            ],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["plan", str(root), "--extra-context", "test context"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("test-project", result.stdout)

    @patch("nxdo.cli.generate_next_tasks")
    def test_typer_plan_command_json_output(self, mock_generate: MagicMock) -> None:
        from nxdo.models import TaskPlan

        mock_plan = TaskPlan(
            project_name="test-project",
            summary="Test plan",
            tasks=[],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["plan", str(root), "--json"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("test-project", result.stdout)

    def test_typer_validate_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            plan_file = Path(tmp_dir) / "invalid.json"
            plan_file.write_text("{invalid json", encoding="utf-8")
            result = runner.invoke(app, ["validate", str(plan_file)])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.stderr.lower() or result.stdout.lower())

    def test_main_module_can_be_imported(self) -> None:
        """Test that __main__.py can be imported without errors."""
        from nxdo import __main__
        self.assertIsNotNone(__main__)

    def test_main_module_has_app_entry(self) -> None:
        """Test that __main__ module exposes app_entry for script execution."""
        from nxdo import __main__
        self.assertTrue(hasattr(__main__, 'app_entry'))
        self.assertTrue(callable(__main__.app_entry))

    @patch("nxdo.cli.generate_next_tasks")
    def test_cmd_plan_handles_value_error(self, mock_generate: MagicMock) -> None:
        """Test that cmd_plan handles ValueError from generate_next_tasks."""
        mock_generate.side_effect = ValueError("Test error")

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            result = runner.invoke(app, ["plan", str(root)])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error", result.stderr)

    @patch("nxdo.cli.app")
    def test_app_entry_calls_app(self, mock_app: MagicMock) -> None:
        """Test that app_entry calls the Typer app."""
        from nxdo.cli import app_entry
        app_entry()
        mock_app.assert_called_once()

    @patch("nxdo.cli.generate_next_tasks")
    def test_main_json_output(self, mock_generate: MagicMock) -> None:
        """Test that main function outputs JSON when --json flag is used."""
        from nxdo.models import TaskPlan
        mock_plan = TaskPlan(
            project_name="test",
            summary="test",
            tasks=[],
        )
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            exit_code = main([str(root), "--json"])
            self.assertEqual(exit_code, 0)

    @patch("nxdo.cli.generate_next_tasks")
    def test_main_plain_output(self, mock_generate: MagicMock) -> None:
        """Test that main function prints plan without --json (line 213)."""
        from nxdo.models import TaskPlan
        mock_plan = TaskPlan(project_name="proj", summary="sum", tasks=[])
        mock_generate.return_value = mock_plan

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root)])
            self.assertEqual(exit_code, 0)
            self.assertIn("proj", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
