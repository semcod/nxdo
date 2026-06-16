import unittest
from unittest.mock import MagicMock, patch

from nxdo.llm_client import build_user_prompt, parse_task_plan_response, OpenAICompatibleLLMClient


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
{"project_name":"nxdo","summary":"Ready","tasks":[{"number":1,"title":"Add CLI","description":"Ship it","priority":"high","task_type":"feature","estimated_hours":2,"acceptance_criteria":["CLI works"],"dependencies":[]}]}
```"""

        plan = parse_task_plan_response(raw, "nxdo", "demo-model")

        self.assertEqual(plan.project_name, "nxdo")
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

    @patch("nxdo.llm_client.OpenAICompatProvider")
    def test_openai_llm_client_initialization(self, mock_provider: MagicMock) -> None:
        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance
        mock_provider_instance.api_key = "test-key"
        mock_provider_instance.model = "test-model"
        mock_provider_instance.base_url = "http://test"

        client = OpenAICompatibleLLMClient(
            api_key="test-key",
            model="test-model",
            base_url="http://test",
        )

        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.model, "test-model")
        self.assertEqual(client.base_url, "http://test")

    @patch("nxdo.llm_client.OpenAICompatProvider")
    def test_openai_llm_client_generate_task_plan(self, mock_provider: MagicMock) -> None:
        from nxdo.models import TaskPlan

        mock_provider_instance = MagicMock()
        mock_provider.return_value = mock_provider_instance
        mock_provider_instance.api_key = "test-key"
        mock_provider_instance.model = "test-model"
        mock_provider_instance.base_url = "http://test"

        mock_plan = TaskPlan(
            project_name="test",
            summary="test",
            tasks=[],
        )
        mock_provider_instance.generate_plan.return_value = mock_plan

        client = OpenAICompatibleLLMClient(api_key="test-key")
        result = client.generate_task_plan("project", "git", "test", "extra")

        self.assertEqual(result.project_name, "test")
        mock_provider_instance.generate_plan.assert_called_once()


if __name__ == "__main__":
    unittest.main()

