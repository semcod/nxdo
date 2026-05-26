import unittest
from unittest.mock import patch, MagicMock

from lane.git_reader import _parse_commits, read_git_context, _run, CommitInfo, GitContext
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

    def test_git_context_to_text_with_commits_and_files(self) -> None:
        commit = CommitInfo(
            hash="abc123",
            author="Alice",
            date="2026-05-26T10:00:00+00:00",
            message="Add feature",
            files_changed=["file1.py", "file2.py"],
        )
        ctx = GitContext(
            repo_path=Path("/tmp"),
            branch="main",
            remote_url="git@github.com:user/repo.git",
            recent_commits=[commit],
            changed_files_summary=["  3x  file1.py"],
            open_todos=[],
        )
        text = ctx.to_text()
        self.assertIn("main", text)
        self.assertIn("git@github.com:user/repo.git", text)
        self.assertIn("Add feature", text)

    def test_git_context_to_text_with_todos(self) -> None:
        ctx = GitContext(
            repo_path=Path("/tmp"),
            branch="main",
            remote_url="no remote",
            recent_commits=[],
            changed_files_summary=[],
            open_todos=["file.py:10: TODO: fix this"],
        )
        text = ctx.to_text()
        self.assertIn("TODO/FIXME markers found in code:", text)
        self.assertIn("file.py:10: TODO: fix this", text)

    def test_commit_info_str_with_many_files(self) -> None:
        commit = CommitInfo(
            hash="abc123",
            author="Alice",
            date="2026-05-26T10:00:00+00:00",
            message="Big change",
            files_changed=[f"file{i}.py" for i in range(10)],
        )
        text = str(commit)
        self.assertIn("+5 more", text)

    @patch("lane.git_reader.subprocess.run")
    def test_run_returns_empty_on_failure(self, mock_run: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = _run(["git", "status"], Path("/tmp"))
        self.assertEqual(result, "")

    @patch("lane.git_reader.subprocess.run")
    def test_run_returns_empty_on_timeout(self, mock_run: MagicMock) -> None:
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("git", 15)

        result = _run(["git", "status"], Path("/tmp"))
        self.assertEqual(result, "")

    @patch("lane.git_reader._run")
    @patch("lane.git_reader._is_git_repo")
    def test_read_git_context_with_real_git_repo(self, mock_is_git: MagicMock, mock_run: MagicMock) -> None:
        mock_is_git.return_value = True
        mock_run.side_effect = [
            "main",  # branch
            "git@github.com:user/repo.git",  # remote
            "abc123|||Alice|||2026-05-26T10:00:00+00:00|||Commit message\nfile1.py\nfile2.py",  # log
            "file1.py\nfile2.py\nfile1.py",  # file frequency
            "file.py:10: TODO: fix this",  # grep
        ]

        ctx = read_git_context(Path("/fake/repo"), max_commits=10)

        self.assertEqual(ctx.branch, "main")
        self.assertEqual(ctx.remote_url, "git@github.com:user/repo.git")
        self.assertEqual(len(ctx.recent_commits), 1)
        self.assertEqual(len(ctx.changed_files_summary), 2)
        self.assertEqual(len(ctx.open_todos), 1)

    @patch("lane.git_reader._run")
    @patch("lane.git_reader._is_git_repo")
    def test_read_git_context_with_empty_git_log(self, mock_is_git: MagicMock, mock_run: MagicMock) -> None:
        mock_is_git.return_value = True
        mock_run.side_effect = [
            "main",  # branch
            "git@github.com:user/repo.git",  # remote
            "",  # empty log
            "",  # empty file frequency
            "",  # empty grep
        ]

        ctx = read_git_context(Path("/fake/repo"), max_commits=10)

        self.assertEqual(len(ctx.recent_commits), 0)
        self.assertEqual(len(ctx.changed_files_summary), 0)
        self.assertEqual(len(ctx.open_todos), 0)


if __name__ == "__main__":
    unittest.main()

