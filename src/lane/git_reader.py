"""Read recent git history and repository metadata."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class CommitInfo:
    hash: str
    author: str
    date: str
    message: str
    files_changed: list[str]

    def __str__(self) -> str:
        files = ", ".join(self.files_changed[:5])
        suffix = f" (+{len(self.files_changed) - 5} more)" if len(self.files_changed) > 5 else ""
        return f"{self.date[:10]} [{self.hash[:7]}] {self.message} ({files}{suffix})"


@dataclass
class GitContext:
    repo_path: Path
    branch: str
    remote_url: str
    recent_commits: list[CommitInfo]
    changed_files_summary: list[str]
    open_todos: list[str]

    def to_text(self) -> str:
        lines = [
            f"Branch: {self.branch}",
            f"Remote: {self.remote_url}",
            "",
            f"Recent {len(self.recent_commits)} commits:",
        ]
        if self.recent_commits:
            for commit in self.recent_commits:
                lines.append(f"  {commit}")
        else:
            lines.append("  (no commits found)")
        lines += ["", "Most active files recently:"]
        if self.changed_files_summary:
            for changed_file in self.changed_files_summary[:15]:
                lines.append(f"  {changed_file}")
        else:
            lines.append("  (no file activity found)")
        if self.open_todos:
            lines += ["", "TODO/FIXME markers found in code:"]
            for todo in self.open_todos[:20]:
                lines.append(f"  {todo}")
        return "\n".join(lines)


def _run(cmd: list[str], cwd: Path) -> str:
    """Run *cmd* in *cwd* and return stdout; return empty string on any failure."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _is_git_repo(path: Path) -> bool:
    """Return True if *path* is inside a git repository."""
    return bool(_run(["git", "rev-parse", "--git-dir"], path))


def _get_git_branch(repo_path: Path) -> str:
    """Get the current git branch name."""
    return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_path) or "unknown"


def _get_git_remote(repo_path: Path) -> str:
    """Get the git remote URL."""
    return _run(["git", "remote", "get-url", "origin"], repo_path) or "no remote"


def _get_git_commits(repo_path: Path, max_commits: int) -> list[CommitInfo]:
    """Get recent git commits."""
    log_raw = _run(
        [
            "git",
            "log",
            f"-{max_commits}",
            "--pretty=format:%H|||%an|||%aI|||%s",
            "--name-only",
        ],
        repo_path,
    )
    return _parse_commits(log_raw)


def _get_file_frequency(repo_path: Path, max_commits: int) -> list[str]:
    """Get file change frequency summary."""
    freq_raw = _run(
        ["git", "log", f"-{max_commits}", "--name-only", "--pretty=format:"],
        repo_path,
    )
    file_freq: dict[str, int] = {}
    for line in freq_raw.splitlines():
        line = line.strip()
        if line:
            file_freq[line] = file_freq.get(line, 0) + 1
    return [
        f"{count:3d}x  {path}"
        for path, count in sorted(file_freq.items(), key=lambda item: (-item[1], item[0]))
    ]


def _get_git_todos(repo_path: Path) -> list[str]:
    """Get TODO/FIXME markers from git grep."""
    grep_raw = _run(["git", "grep", "-n", "-E", "TODO|FIXME|HACK|XXX"], repo_path)
    return [line for line in grep_raw.splitlines() if line.strip()]


def _create_empty_context(repo_path: Path) -> GitContext:
    """Create an empty GitContext for non-git repositories."""
    return GitContext(
        repo_path=repo_path,
        branch="unknown",
        remote_url="no remote",
        recent_commits=[],
        changed_files_summary=[],
        open_todos=[],
    )


def read_git_context(repo_path: Path, max_commits: int = 30) -> GitContext:
    if not _is_git_repo(repo_path):
        return _create_empty_context(repo_path)

    branch = _get_git_branch(repo_path)
    remote_url = _get_git_remote(repo_path)
    recent_commits = _get_git_commits(repo_path, max_commits)
    changed_files_summary = _get_file_frequency(repo_path, max_commits)
    open_todos = _get_git_todos(repo_path)

    return GitContext(
        repo_path=repo_path,
        branch=branch,
        remote_url=remote_url,
        recent_commits=recent_commits,
        changed_files_summary=changed_files_summary,
        open_todos=open_todos,
    )


def _parse_commit_metadata(line: str) -> tuple[str, str, str, str] | None:
    """Parse a commit metadata line and return hash, author, date, message."""
    if "|||" not in line:
        return None
    parts = line.split("|||", 3)
    message = parts[3] if len(parts) > 3 else ""
    return (parts[0], parts[1], parts[2], message)


def _create_commit_info(meta: tuple[str, str, str, str], files: list[str]) -> CommitInfo:
    """Create a CommitInfo object from metadata and files."""
    commit_hash, author, date, message = meta
    return CommitInfo(commit_hash, author, date, message, files)


def _parse_commits(log_raw: str) -> list[CommitInfo]:
    commits: list[CommitInfo] = []
    current_meta: tuple[str, str, str, str] | None = None
    current_files: list[str] = []

    for line in log_raw.splitlines():
        meta = _parse_commit_metadata(line)
        if meta:
            if current_meta:
                commits.append(_create_commit_info(current_meta, current_files))
            current_meta = meta
            current_files = []
        elif line.strip() and current_meta:
            current_files.append(line.strip())

    if current_meta:
        commits.append(_create_commit_info(current_meta, current_files))

    return commits

