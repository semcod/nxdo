import unittest

from lane.git_reader import _parse_commits


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


if __name__ == "__main__":
    unittest.main()

