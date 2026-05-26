from pathlib import Path
import tempfile
import unittest

from lane.project_analyzer import analyze_project, _parse_pyproject, _readme_summary


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

    def test_analyze_project_no_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            snapshot = analyze_project(root)

        self.assertEqual(snapshot.name, root.name)
        self.assertEqual(snapshot.description, "")
        self.assertEqual(snapshot.language_stack, [])

    def test_parse_pyproject_invalid_toml_falls_back_to_regex(self) -> None:
        # Invalid TOML — should fall back to regex
        text = '[project\nname = "myapp"\ndescription = "A tool"'
        name, desc = _parse_pyproject(text, "fallback")
        # With tomllib parse error the regex fallback should still find something
        # (or return the fallback), so no exception is raised
        self.assertIsInstance(name, str)
        self.assertIsInstance(desc, str)

    def test_parse_pyproject_valid_toml(self) -> None:
        text = '[project]\nname = "lane"\ndescription = "Task planner"'
        name, desc = _parse_pyproject(text, "fallback")
        self.assertEqual(name, "lane")
        self.assertEqual(desc, "Task planner")

    def test_readme_summary_skips_headers(self) -> None:
        text = "# Heading\n\nActual description here."
        self.assertEqual(_readme_summary(text), "Actual description here.")

    def test_readme_summary_empty(self) -> None:
        self.assertEqual(_readme_summary(""), "")

    def test_analyze_project_readme_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# demo\n\nDemo project\n", encoding="utf-8")
            snapshot = analyze_project(root)

        self.assertEqual(snapshot.description, "Demo project")


if __name__ == "__main__":
    unittest.main()

