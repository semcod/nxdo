"""Tests for lane.providers."""

import json
import unittest
from unittest.mock import MagicMock, patch

from lane.providers.openai_compat import OpenAICompatProvider, _parse_response


_VALID_RAW = json.dumps({
    "project_name": "demo",
    "summary": "A good project.",
    "tasks": [
        {
            "number": 1,
            "title": "Add tests",
            "description": "Improve coverage.",
            "priority": "high",
            "task_type": "test",
            "estimated_hours": 3,
            "acceptance_criteria": ["Coverage > 80%"],
            "dependencies": [],
        }
    ],
})


class ParseResponseTests(unittest.TestCase):
    def test_valid_response_parsed(self) -> None:
        plan = _parse_response(_VALID_RAW, "demo", "model-x")
        self.assertEqual(plan.project_name, "demo")
        self.assertEqual(len(plan.tasks), 1)
        self.assertEqual(plan.tasks[0].title, "Add tests")

    def test_invalid_json_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _parse_response("not json", "p", "m")
        self.assertIn("invalid JSON", str(ctx.exception))

    def test_non_object_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            _parse_response(json.dumps([1, 2, 3]), "p", "m")
        self.assertIn("JSON object", str(ctx.exception))

    def test_bad_task_priority_raises(self) -> None:
        raw = json.dumps({
            "project_name": "p",
            "summary": "s",
            "tasks": [{"number": 1, "title": "T", "description": "D", "priority": "NOPE"}],
        })
        with self.assertRaises(ValueError) as ctx:
            _parse_response(raw, "p", "m")
        self.assertIn("Invalid task data", str(ctx.exception))

    def test_fenced_code_block_stripped(self) -> None:
        raw = f"```json\n{_VALID_RAW}\n```"
        plan = _parse_response(raw, "demo", "m")
        self.assertEqual(plan.project_name, "demo")


class OpenAICompatProviderTests(unittest.TestCase):
    def test_no_api_key_raises_value_error(self) -> None:
        provider = OpenAICompatProvider(api_key=None)
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                provider._call_api("prompt")
        self.assertIn("API key", str(ctx.exception))

    def test_generate_plan_uses_parse_response(self) -> None:
        provider = OpenAICompatProvider(api_key="sk-test")
        with patch.object(provider, "_call_api", return_value=_VALID_RAW):
            plan = provider.generate_plan("prompt", "demo")
        self.assertEqual(plan.project_name, "demo")
        self.assertEqual(len(plan.tasks), 1)


if __name__ == "__main__":
    unittest.main()
