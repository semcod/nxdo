import unittest

from lane.git_reader import _parse_commits, read_git_context
from pathlib import Path
import tempfile


class GitReaderTests(unittest.TestCase):
    def test_parse_commits_keeps_files_with_each_commit(self) -> None:
        log_raw = "\n".join(
            [
                "abc123|||Alice|||2026-05-26T10:00:00+00:00|||Add planner",
                "src/lane/cli.py",
                "README.md",
                "def456|||Bob|||2026-05-25T09:00:00+00:00|||Fix tests",
                "tests/test_cli.py",
            ]
        )

        commits = _parse_commits(log_raw)

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].files_changed, ["src/lane/cli.py", "README.md"])
        self.assertEqual(commits[1].message, "Fix tests")

    def test_parse_commits_empty_log(self) -> None:
        commits = _parse_commits("")
        self.assertEqual(commits, [])

    def test_parse_commits_single_commit_no_files(self) -> None:
        commits = _parse_commits("abc123|||Alice|||2026-05-26T10:00:00+00:00|||Initial commit")
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].files_changed, [])

    def test_read_git_context_non_git_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ctx = read_git_context(Path(tmp_dir))

        self.assertEqual(ctx.branch, "unknown")
        self.assertEqual(ctx.remote_url, "no remote")
        self.assertEqual(ctx.recent_commits, [])
        self.assertEqual(ctx.changed_files_summary, [])

    def test_git_context_to_text_no_commits(self) -> None:
        from lane.git_reader import GitContext

        ctx = GitContext(
            repo_path=Path("/tmp"),
            branch="main",
            remote_url="no remote",
            recent_commits=[],
            changed_files_summary=[],
            open_todos=[],
        )
        text = ctx.to_text()
        self.assertIn("no commits found", text)
        self.assertIn("no file activity found", text)


if __name__ == "__main__":
    unittest.main()

