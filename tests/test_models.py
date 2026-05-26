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


if __name__ == "__main__":
    unittest.main()

