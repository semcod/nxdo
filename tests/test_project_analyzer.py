from pathlib import Path
import tempfile
import unittest

from lane.project_analyzer import analyze_project


class ProjectAnalyzerTests(unittest.TestCase):
    def test_analyze_project_reads_pyproject_and_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "pyproject.toml").write_text(
                "\n".join(
                    [
                        "[project]",
                        'name = "lane"',
                        'description = "Task planner"',
                    ]
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("# lane\n\nTask planner\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "demo.py").write_text("print('ok')\n", encoding="utf-8")

            snapshot = analyze_project(root)

        self.assertEqual(snapshot.name, "lane")
        self.assertEqual(snapshot.description, "Task planner")
        self.assertIn("Python", snapshot.language_stack)
        self.assertIn("README.md", snapshot.file_contents)
        self.assertIn("src", snapshot.directory_tree)


if __name__ == "__main__":
    unittest.main()

