from pathlib import Path
import tempfile
import unittest

from nxdo.project_analyzer import (
    analyze_project,
    _parse_pyproject,
    _parse_pyproject_tomllib,
    _readme_summary,
    _parse_package_json,
    _parse_cargo,
    _detect_stack,
    _build_tree,
    _should_ignore_entry,
)


class ProjectAnalyzerTests(unittest.TestCase):
    def test_analyze_project_reads_pyproject_and_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "pyproject.toml").write_text(
                "\n".join(
                    [
                        "[project]",
                        'name = "nxdo"',
                        'description = "Task planner"',
                    ]
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("# nxdo\n\nTask planner\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "demo.py").write_text("print('ok')\n", encoding="utf-8")

            snapshot = analyze_project(root)

        self.assertEqual(snapshot.name, "nxdo")
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
        text = '[project]\nname = "nxdo"\ndescription = "Task planner"'
        name, desc = _parse_pyproject(text, "fallback")
        self.assertEqual(name, "nxdo")
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

    def test_parse_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            pkg_file = root / "package.json"
            pkg_file.write_text('{"name": "myapp", "description": "A JS app"}', encoding="utf-8")
            name, desc = _parse_package_json(pkg_file, "fallback")
        self.assertEqual(name, "myapp")
        self.assertEqual(desc, "A JS app")

    def test_parse_package_json_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            pkg_file = root / "package.json"
            pkg_file.write_text("{invalid json", encoding="utf-8")
            name, desc = _parse_package_json(pkg_file, "fallback")
        self.assertEqual(name, "fallback")
        self.assertEqual(desc, "")

    def test_parse_cargo_toml(self) -> None:
        text = 'name = "mycrate"\ndescription = "A Rust crate"'
        name, desc = _parse_cargo(text, "fallback")
        self.assertEqual(name, "mycrate")
        self.assertEqual(desc, "A Rust crate")

    def test_detect_stack_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
            stack = _detect_stack(root)
        self.assertIn("Python", stack)

    def test_detect_stack_javascript(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "package.json").write_text("{}", encoding="utf-8")
            stack = _detect_stack(root)
        self.assertIn("JavaScript/TypeScript", stack)

    def test_detect_stack_rust(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "Cargo.toml").write_text("", encoding="utf-8")
            stack = _detect_stack(root)
        self.assertIn("Rust", stack)

    def test_detect_stack_by_extension(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("", encoding="utf-8")
            stack = _detect_stack(root)
        self.assertIn("Python", stack)

    def test_analyze_project_handles_oserror_on_file_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            # Create a file that can't be read (simulate by making it unreadable after creation)
            unreadable = root / "pyproject.toml"
            unreadable.write_text("[project]\n", encoding="utf-8")
            # On Unix, make it unreadable
            try:
                unreadable.chmod(0o000)
                snapshot = analyze_project(root)
                # Should still succeed, just skip the unreadable file
                self.assertIsNotNone(snapshot)
            finally:
                # Restore permissions for cleanup
                try:
                    unreadable.chmod(0o644)
                except OSError:
                    pass

    def test_analyze_project_truncates_large_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            large_content = "x" * 4000  # Larger than MAX_FILE_CHARS (3000)
            (root / "README.md").write_text("# test\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text(large_content, encoding="utf-8")
            snapshot = analyze_project(root)
            self.assertIn("truncated", snapshot.file_contents["CHANGELOG.md"])

    def test_analyze_project_uses_package_json_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "package.json").write_text('{"name": "jsapp", "description": "JS app"}', encoding="utf-8")
            snapshot = analyze_project(root)
            self.assertEqual(snapshot.name, "jsapp")
            self.assertEqual(snapshot.description, "JS app")

    def test_analyze_project_uses_cargo_parser(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "Cargo.toml").write_text('name = "rustcrate"\ndescription = "Rust crate"', encoding="utf-8")
            snapshot = analyze_project(root)
            self.assertEqual(snapshot.name, "rustcrate")
            self.assertEqual(snapshot.description, "Rust crate")


    def test_parse_pyproject_tomllib_returns_none_when_tomllib_unavailable(self) -> None:
        """Test _parse_pyproject_tomllib returns None when tomllib is None (line 152)."""
        import nxdo.project_analyzer as pa
        original = pa.tomllib
        pa.tomllib = None
        try:
            result = _parse_pyproject_tomllib('[project]\nname = "x"', "fallback")
            self.assertIsNone(result)
        finally:
            pa.tomllib = original

    def test_parse_pyproject_tomllib_returns_none_when_project_not_dict(self) -> None:
        """Test _parse_pyproject_tomllib returns None when project is not a dict (line 160)."""
        result = _parse_pyproject_tomllib("project = 42\n", "fallback")
        self.assertIsNone(result)

    def test_build_tree_returns_empty_on_oserror(self) -> None:
        """Test _build_tree returns empty string on OSError (lines 242-243)."""
        from pathlib import Path
        result = _build_tree(Path("/nonexistent/path/xyz"), max_depth=3)
        self.assertEqual(result, "")

    def test_build_tree_ignores_generated_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "src").mkdir()
            (root / "src" / "demo.py").write_text("", encoding="utf-8")
            (root / "project").mkdir()
            (root / "project" / "flow.png").write_text("", encoding="utf-8")
            (root / "uv.lock").write_text("", encoding="utf-8")
            (root / "nxdo.egg-info").mkdir()
            (root / "nxdo.egg-info" / "PKG-INFO").write_text("", encoding="utf-8")

            tree = _build_tree(root, max_depth=3)

        self.assertIn("demo.py", tree)
        self.assertIn("project", tree)
        self.assertNotIn("flow.png", tree)
        self.assertNotIn("uv.lock", tree)
        self.assertNotIn("nxdo.egg-info", tree)

    def test_should_ignore_entry_filters_generated_names(self) -> None:
        self.assertTrue(_should_ignore_entry(".planfile"))
        self.assertTrue(_should_ignore_entry("package.egg-info"))
        self.assertTrue(_should_ignore_entry("diagram.png"))
        self.assertTrue(_should_ignore_entry("uv.lock"))
        self.assertFalse(_should_ignore_entry("pyproject.toml"))


if __name__ == "__main__":
    unittest.main()
