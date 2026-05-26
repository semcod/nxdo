from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from lane.cli import app, app_entry, main
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
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            import os

            env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                exit_code = main([str(root)])

        self.assertEqual(exit_code, 1)

    def test_print_context_raw_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root), "--print-prompt", "--max-commits", "1"])
                output = stdout.getvalue()
                self.assertIn("Project:", output)

    def test_json_mode_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            import os

            env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                exit_code = main([str(root), "--json"])
                self.assertEqual(exit_code, 1)  # No API key, so fails

    def test_max_commits_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as stdout:
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

    @patch("lane.cli.generate_next_tasks")
    def test_typer_plan_command_with_mocked_provider(self, mock_generate: MagicMock) -> None:
        from lane.models import TaskPlan, Task, Priority, TaskType

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

    @patch("lane.cli.generate_next_tasks")
    def test_typer_plan_command_json_output(self, mock_generate: MagicMock) -> None:
        from lane.models import TaskPlan

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


if __name__ == "__main__":
    unittest.main()
