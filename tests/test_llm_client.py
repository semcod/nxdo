import unittest

from lane.llm_client import build_user_prompt, parse_task_plan_response


class LLMClientTests(unittest.TestCase):
    def test_build_user_prompt_includes_sections(self) -> None:
        prompt = build_user_prompt("project", "git", "extra")

        self.assertIn("=== PROJECT STATE ===", prompt)
        self.assertIn("=== GIT HISTORY ===", prompt)
        self.assertIn("extra", prompt)

    def test_parse_task_plan_response_strips_fences(self) -> None:
        raw = """```json
{"project_name":"lane","summary":"Ready","tasks":[{"number":1,"title":"Add CLI","description":"Ship it","priority":"high","task_type":"feature","estimated_hours":2,"acceptance_criteria":["CLI works"],"dependencies":[]}]}
```"""

        plan = parse_task_plan_response(raw, "lane", "demo-model")

        self.assertEqual(plan.project_name, "lane")
        self.assertEqual(plan.tasks[0].priority.value, "high")
        self.assertEqual(plan.model_used, "demo-model")


if __name__ == "__main__":
    unittest.main()

