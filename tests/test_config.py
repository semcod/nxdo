"""Tests for lane.config."""

import os
import unittest
from unittest.mock import patch


class ConfigTests(unittest.TestCase):
    def test_settings_reads_openrouter_key(self) -> None:
        from lane.config import LaneSettings

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test-123"}, clear=False):
            cfg = LaneSettings()
        self.assertEqual(cfg.openrouter_api_key, "sk-test-123")
        self.assertEqual(cfg.api_key, "sk-test-123")

    def test_settings_prefers_openrouter_over_openai(self) -> None:
        from lane.config import LaneSettings

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or", "OPENAI_API_KEY": "sk-oa"}, clear=False):
            cfg = LaneSettings()
        self.assertEqual(cfg.api_key, "sk-or")

    def test_settings_falls_back_to_openai_key(self) -> None:
        from lane.config import LaneSettings

        env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
        env["OPENAI_API_KEY"] = "sk-oa-only"
        with patch.dict(os.environ, env, clear=True):
            cfg = LaneSettings(_env_file=None)
        self.assertEqual(cfg.api_key, "sk-oa-only")

    def test_settings_api_key_none_when_no_key_set(self) -> None:
        from lane.config import LaneSettings

        env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            cfg = LaneSettings(_env_file=None)
        self.assertIsNone(cfg.api_key)

    def test_settings_defaults(self) -> None:
        from lane.config import LaneSettings

        cfg = LaneSettings()
        self.assertEqual(cfg.max_commits, 30)
        self.assertEqual(cfg.llm_timeout, 60)
        self.assertEqual(cfg.llm_max_retries, 3)


if __name__ == "__main__":
    unittest.main()
