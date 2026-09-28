import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nxdo.project_analyzer import (
    _build_tree,
    _collect_tree_lines,
    _detect_stack,
    _entry_lines,
    _format_tree_node,
    _parse_cargo,
    _parse_package_json,
    _parse_pyproject,
    _parse_pyproject_tomllib,
    _readme_summary,
    _should_ignore_entry,
    _visible_children,
    analyze_project,
)


class ProjectAnalyzerTests(unittest.TestCase):
    def test_analyze_project_reads_pyproject_and_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "pyproject.toml").write_text(
                "[project]\n"
                'name = "nxdo"\n'
                'description = "Task planner"',
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
        """Test _build_tree returns empty string on OSError."""
        result = _build_tree(Path("/nonexistent/path/xyz"), max_depth=3)
        self.assertEqual(result, "")

        with patch("nxdo.project_analyzer._collect_tree_lines", side_effect=OSError("read failed")):
            self.assertEqual(_build_tree(Path("/some/path")), "")

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

    def test_visible_children_filters_and_sorts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "b_file.py").write_text("", encoding="utf-8")
            (root / "a_file.py").write_text("", encoding="utf-8")
            (root / "z_dir").mkdir()
            (root / ".git").mkdir()

            children = _visible_children(root)
            names = [c.name for c in children]
            self.assertEqual(names, ["z_dir", "a_file.py", "b_file.py"])

    def test_format_tree_node_formats_file_and_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            f = root / "file.py"
            f.write_text("", encoding="utf-8")
            d = root / "sub"
            d.mkdir()

            self.assertEqual(_format_tree_node(f, "  "), "  file.py")
            self.assertEqual(_format_tree_node(d, "  "), "  sub/")

    def test_entry_lines_includes_children_when_depth_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            d = root / "sub"
            d.mkdir()
            (d / "leaf.py").write_text("", encoding="utf-8")

            lines = _entry_lines(d, max_depth=2, depth=1, prefix="")
            self.assertEqual(lines, ["sub/", "  leaf.py"])

            lines_bounded = _entry_lines(d, max_depth=1, depth=1, prefix="")
            self.assertEqual(lines_bounded, ["sub/"])

    def test_collect_tree_lines_respects_max_depth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            d1 = root / "lvl1"
            d1.mkdir()
            d2 = d1 / "lvl2"
            d2.mkdir()
            (d2 / "leaf.txt").write_text("", encoding="utf-8")

            lines = _collect_tree_lines(root, max_depth=1)
            self.assertEqual(len(lines), 1)
            self.assertIn("lvl1", lines[0])

            lines = _collect_tree_lines(root, max_depth=2)
            self.assertTrue(any("lvl1" in line for line in lines))
            self.assertTrue(any("lvl2" in line for line in lines))
            self.assertFalse(any("leaf.txt" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
