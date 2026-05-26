import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from lane.models import TaskPlan
from lane.planner import generate_next_tasks


class PlannerTests(unittest.TestCase):
    @patch("lane.planner.analyze_project")
    @patch("lane.planner.read_git_context")
    @patch("lane.planner.build_user_prompt")
    def test_generate_next_tasks_calls_provider(
        self,
        mock_build_prompt: MagicMock,
        mock_read_git: MagicMock,
        mock_analyze: MagicMock,
    ) -> None:
        from lane.config import LaneSettings
        from lane.providers import LLMProvider

        mock_snapshot = MagicMock()
        mock_snapshot.name = "test-project"
        mock_snapshot.to_text.return_value = "Project text"
        mock_analyze.return_value = mock_snapshot

        mock_git_ctx = MagicMock()
        mock_git_ctx.to_text.return_value = "Git text"
        mock_read_git.return_value = mock_git_ctx

        mock_build_prompt.return_value = "Full prompt"

        mock_provider = MagicMock(spec=LLMProvider)
        mock_plan = TaskPlan(
            project_name="test-project",
            summary="Test summary",
            tasks=[],
        )
        mock_provider.generate_plan.return_value = mock_plan

        result = generate_next_tasks(
            repo_path=Path("/fake/repo"),
            provider=mock_provider,
            settings=LaneSettings(),
        )

        mock_provider.generate_plan.assert_called_once_with("Full prompt", project_name="test-project")
        self.assertEqual(result.project_name, "test-project")

    @patch("lane.planner.analyze_project")
    @patch("lane.planner.read_git_context")
    @patch("lane.planner.build_user_prompt")
    def test_generate_next_tasks_uses_default_provider_when_none(
        self,
        mock_build_prompt: MagicMock,
        mock_read_git: MagicMock,
        mock_analyze: MagicMock,
    ) -> None:
        from lane.config import LaneSettings

        mock_snapshot = MagicMock()
        mock_snapshot.name = "test-project"
        mock_snapshot.to_text.return_value = "Project text"
        mock_analyze.return_value = mock_snapshot

        mock_git_ctx = MagicMock()
        mock_git_ctx.to_text.return_value = "Git text"
        mock_read_git.return_value = mock_git_ctx

        mock_build_prompt.return_value = "Full prompt"

        with patch("lane.planner.OpenAICompatProvider") as mock_provider_class:
            mock_provider = MagicMock()
            mock_plan = TaskPlan(
                project_name="test-project",
                summary="Test summary",
                tasks=[],
            )
            mock_provider.generate_plan.return_value = mock_plan
            mock_provider_class.return_value = mock_provider

            result = generate_next_tasks(
                repo_path=Path("/fake/repo"),
                settings=LaneSettings(),
            )

            mock_provider_class.assert_called_once()
            self.assertEqual(result.project_name, "test-project")


if __name__ == "__main__":
    unittest.main()
