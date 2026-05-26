import unittest

from lane.llm_client import build_user_prompt, parse_task_plan_response


class LLMClientTests(unittest.TestCase):
    def test_build_user_prompt_includes_sections(self) -> None:
        prompt = build_user_prompt("project", "git", "extra")

        self.assertIn("=== PROJECT STATE ===", prompt)
        self.assertIn("=== GIT HISTORY ===", prompt)
        self.assertIn("extra", prompt)

    def test_build_user_prompt_default_extra_context(self) -> None:
        prompt = build_user_prompt("project", "git")
        self.assertIn("None provided.", prompt)

    def test_parse_task_plan_response_strips_fences(self) -> None:
        raw = """```json
{"project_name":"lane","summary":"Ready","tasks":[{"number":1,"title":"Add CLI","description":"Ship it","priority":"high","task_type":"feature","estimated_hours":2,"acceptance_criteria":["CLI works"],"dependencies":[]}]}
```"""

        plan = parse_task_plan_response(raw, "lane", "demo-model")

        self.assertEqual(plan.project_name, "lane")
        self.assertEqual(plan.tasks[0].priority.value, "high")
        self.assertEqual(plan.model_used, "demo-model")

    def test_parse_task_plan_response_invalid_json_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            parse_task_plan_response("not json at all", "p", "m")
        self.assertIn("invalid JSON", str(ctx.exception))

    def test_parse_task_plan_response_non_object_raises(self) -> None:
        import json

        with self.assertRaises(ValueError) as ctx:
            parse_task_plan_response(json.dumps([1, 2, 3]), "p", "m")
        self.assertIn("JSON object", str(ctx.exception))

    def test_parse_task_plan_response_falls_back_to_project_name(self) -> None:
        import json

        raw = json.dumps({"summary": "s", "tasks": []})
        plan = parse_task_plan_response(raw, "fallback_name", "m")
        self.assertEqual(plan.project_name, "fallback_name")

    def test_parse_task_plan_response_invalid_priority_raises(self) -> None:
        import json

        raw = json.dumps({
            "project_name": "p",
            "summary": "s",
            "tasks": [{"number": 1, "title": "T", "description": "D", "priority": "SUPER_HIGH"}],
        })
        with self.assertRaises(ValueError):
            parse_task_plan_response(raw, "p", "m")


if __name__ == "__main__":
    unittest.main()

