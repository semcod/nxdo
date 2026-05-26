import unittest

from lane.models import Priority, Task, TaskPlan, TaskType


class TaskModelTests(unittest.TestCase):
    def test_task_string_contains_metadata(self) -> None:
        task = Task(
            number=1,
            title="Implement CLI",
            description="Add an entry point.",
            priority=Priority.HIGH,
            task_type=TaskType.FEATURE,
            estimated_hours=3,
        )

        self.assertEqual(str(task), "01. [FEATURE] (high) ~3h Implement CLI")

    def test_task_string_fractional_hours(self) -> None:
        task = Task(number=2, title="Fix bug", description="Desc", estimated_hours=1.5)
        self.assertIn("~1.5h", str(task))

    def test_task_string_no_hours(self) -> None:
        task = Task(number=3, title="No estimate", description="Desc")
        self.assertNotIn("h ", str(task))

    def test_task_plan_to_dict_serializes_enums(self) -> None:
        plan = TaskPlan(
            project_name="lane",
            summary="summary",
            tasks=[Task(number=1, title="One", description="Desc")],
            model_used="demo",
        )

        data = plan.to_dict()

        self.assertEqual(data["tasks"][0]["priority"], "medium")
        self.assertEqual(data["tasks"][0]["task_type"], "feature")

    def test_task_plan_str_contains_header(self) -> None:
        plan = TaskPlan(
            project_name="myproject",
            summary="This is a summary.",
            tasks=[
                Task(
                    number=1,
                    title="Do something",
                    description="Details.",
                    acceptance_criteria=["Must work"],
                    dependencies=[],
                )
            ],
        )
        text = str(plan)
        self.assertIn("myproject", text)
        self.assertIn("Must work", text)

    def test_task_plan_str_shows_dependencies(self) -> None:
        plan = TaskPlan(
            project_name="p",
            summary="s",
            tasks=[Task(number=2, title="T", description="D", dependencies=[1])],
        )
        self.assertIn("Dependencies", str(plan))

    def test_task_pydantic_validation_rejects_bad_priority(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            Task(number=1, title="T", description="D", priority="invalid_priority")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()

