from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lane.cli import main


class CLITests(unittest.TestCase):
    def test_print_prompt_mode_outputs_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# demo\n\nDemo repository\n", encoding="utf-8")
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root), "--print-prompt", "--max-commits", "1"])

        self.assertEqual(exit_code, 0)
        self.assertIn("=== PROJECT STATE ===", stdout.getvalue())

    def test_print_prompt_includes_extra_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main([str(root), "--print-prompt", "--extra-context", "special question"])

        self.assertEqual(exit_code, 0)
        self.assertIn("special question", stdout.getvalue())

    def test_missing_api_key_returns_exit_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            import os

            env = {k: v for k, v in os.environ.items() if k not in ("OPENROUTER_API_KEY", "OPENAI_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                exit_code = main([str(root)])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
