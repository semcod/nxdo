"""Integration tests for CLI commands: metrics and validate."""

import json

from typer.testing import CliRunner

from nxdo.cli import app

runner = CliRunner()


class TestMetricsCommand:
    def test_metrics_runs_on_temp_repo(self, tmp_path) -> None:
        (tmp_path / "mod.py").write_text("def f():\n    return 1\n")
        result = runner.invoke(app, ["metrics", str(tmp_path)])
        assert result.exit_code == 0
        assert "Code Metrics" in result.stdout

    def test_metrics_top_option(self, tmp_path) -> None:
        (tmp_path / "mod.py").write_text("def f():\n    return 1\n")
        result = runner.invoke(app, ["metrics", str(tmp_path), "--top", "2"])
        assert result.exit_code == 0


class TestValidateCommand:
    def _write_plan(self, tmp_path, payload) -> str:
        p = tmp_path / "plan.json"
        p.write_text(json.dumps(payload))
        return str(p)

    def test_validate_valid_plan(self, tmp_path) -> None:
        plan = {
            "project_name": "demo",
            "summary": "s",
            "generated_at": "2026-01-01 00:00 UTC",
            "tasks": [
                {
                    "number": 1,
                    "title": "T",
                    "description": "d",
                    "priority": "low",
                    "task_type": "chore",
                }
            ],
        }
        result = runner.invoke(app, ["validate", self._write_plan(tmp_path, plan)])
        assert result.exit_code == 0
        assert "is valid" in result.stdout

    def test_validate_invalid_json(self, tmp_path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("{not json")
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code == 1
        assert "Validation failed" in result.stderr + result.stdout

    def test_validate_schema_violation(self, tmp_path) -> None:
        result = runner.invoke(app, ["validate", self._write_plan(tmp_path, {"nope": 1})])
        assert result.exit_code == 1
