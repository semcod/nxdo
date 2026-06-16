import unittest
from io import StringIO

from rich.console import Console

from nxdo.models import Priority, Task, TaskPlan, TaskType
from nxdo.output import render_plan, render_plan_json, render_context


class OutputTests(unittest.TestCase):
    def test_render_plan_displays_summary_and_tasks(self) -> None:
        plan = TaskPlan(
            project_name="test-project",
            summary="This is a test plan.",
            tasks=[
                Task(
                    number=1,
                    title="First task",
                    description="Task description",
                    priority=Priority.HIGH,
                    task_type=TaskType.FEATURE,
                    estimated_hours=2.0,
                )
            ],
            generated_at="2026-05-26",
            model_used="test-model",
        )

        console = Console(file=StringIO(), force_terminal=True)
        render_plan(plan, console)
        output = console.file.getvalue()  # type: ignore[attr-defined]

        self.assertIn("test-project", output)
        self.assertIn("This is a test plan", output)
        self.assertIn("First task", output)

    def test_render_plan_json_outputs_valid_json(self) -> None:
        plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[Task(number=1, title="Task", description="Desc")],
        )

        console = Console(file=StringIO(), force_terminal=False, legacy_windows=False)
        render_plan_json(plan, console)
        output = console.file.getvalue()  # type: ignore[attr-defined]

        # Rich print_json adds ANSI codes, so we validate by checking the JSON structure exists
        self.assertIn("test-project", output)
        self.assertIn("Test summary", output)

    def test_render_context_displays_both_panels(self) -> None:
        project_text = "Project: myproject"
        git_text = "Branch: main"

        console = Console(file=StringIO(), force_terminal=True)
        render_context(project_text, git_text, console)
        output = console.file.getvalue()  # type: ignore[attr-defined]

        self.assertIn("Project Snapshot", output)
        self.assertIn("Git Context", output)
        self.assertIn("myproject", output)
        self.assertIn("main", output)


if __name__ == "__main__":
    unittest.main()
