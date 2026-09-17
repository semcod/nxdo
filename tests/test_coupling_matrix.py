"""Regression tests for nxdo.metrics.coupling.collect_coupling_matrix."""

import subprocess
from pathlib import Path

from nxdo.metrics.coupling import collect_coupling_matrix


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    return repo


def _commit(repo: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(content)
        _git(repo, "add", name)
    _git(repo, "commit", "-qm", "c")


class TestCollectCouplingMatrix:
    def test_detects_co_changed_pair(self, tmp_path) -> None:
        repo = _make_repo(tmp_path)
        for i in range(3):
            _commit(repo, {"a.py": f"a{i}", "b.py": f"b{i}"})
        _commit(repo, {"solo.py": "x"})

        result = collect_coupling_matrix(repo, min_coupling=0.5)
        assert len(result) == 1
        assert {result[0].file_a, result[0].file_b} == {"a.py", "b.py"}
        assert result[0].coupling_score == 1.0
        assert result[0].commits_together == 3

    def test_below_min_coupling_filtered(self, tmp_path) -> None:
        repo = _make_repo(tmp_path)
        _commit(repo, {"a.py": "1", "b.py": "1"})
        _commit(repo, {"a.py": "2"})
        _commit(repo, {"a.py": "3"})
        _commit(repo, {"b.py": "2"})
        _commit(repo, {"b.py": "3"})

        # a<->b: together=1, min(3,3)=3 -> 0.33 (below 0.5, above 0.3)
        assert collect_coupling_matrix(repo, min_coupling=0.5) == []
        result = collect_coupling_matrix(repo, min_coupling=0.3)
        assert len(result) == 1
        assert result[0].coupling_score == 0.33

    def test_empty_repo_returns_empty(self, tmp_path) -> None:
        repo = _make_repo(tmp_path)
        assert collect_coupling_matrix(repo) == []

    def test_file_filter_excludes_other_extensions(self, tmp_path) -> None:
        repo = _make_repo(tmp_path)
        for i in range(3):
            _commit(repo, {"a.py": f"a{i}", "b.md": f"b{i}", "c.md": f"c{i}"})

        # .py filter keeps only a.py -> no pairs; .md keeps b.md+c.md -> 1 pair
        assert collect_coupling_matrix(repo, file_filter={".py"}) == []
        result = collect_coupling_matrix(repo, file_filter={".md"})
        assert len(result) == 1
        assert {result[0].file_a, result[0].file_b} == {"b.md", "c.md"}
