"""Bug hotspot detection and team knowledge metrics."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HotspotMetrics:
    """Bug hotspot metrics for a file."""
    file_path: str
    bug_fix_commits: int
    total_commits: int
    bug_density: float  # bug_fix_commits / total_commits
    code_churn_lines: int  # Lines added + deleted in last 30 days
    author_count: int  # Number of unique authors (bus factor indicator)
    top_authors: list[tuple[str, int]]  # [(author_name, commit_count), ...]


def _get_file_commits_with_info(
    repo_path: Path,
    file_path: str,
    since: str = "30.days.ago",
) -> tuple[list[tuple[str, str, int]], int]:
    """Get commits for specific file: [(hash, author, added+deleted), ...]."""
    try:
        # Get commit info with stats
        commit_log_result = subprocess.run(
            ["git", "log", f"--since={since}", "--format=%H|%an", "--numstat", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if commit_log_result.returncode != 0:
            return [], 0
        
        commits = []
        current_author = ""
        churn = 0
        
        for line in commit_log_result.stdout.strip().split("\n"):
            if "|" in line and not line.startswith("\t"):
                # Commit hash|author line
                parts = line.split("|")
                if len(parts) >= 2:
                    current_author = parts[1].strip()
                    commits.append((parts[0], current_author, 0))
            elif line.strip() and "\t" in line:
                # numstat line: added\tdeleted\tfile
                stats = line.split("\t")
                if len(stats) >= 2:
                    try:
                        added = int(stats[0]) if stats[0] != "-" else 0
                        deleted = int(stats[1]) if stats[1] != "-" else 0
                        churn += added + deleted
                        if commits:
                            # Update churn for current commit
                            h, a, c = commits[-1]
                            commits[-1] = (h, a, c + added + deleted)
                    except ValueError:
                        pass
        
        return commits, churn
    except OSError:
        return [], 0


def _get_bug_fix_commits(repo_path: Path, file_path: str, since: str = "90.days.ago") -> int:
    """Count commits mentioning bug/fix/repair for specific file."""
    bug_patterns = ["fix", "bug", "repair", "hotfix", "patch", "resolve", "issue"]
    
    try:
        bug_log_result = subprocess.run(
            ["git", "log", f"--since={since}", "--format=%H", "-i",
             *(f"--grep={pattern}" for pattern in bug_patterns), "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if bug_log_result.returncode != 0:
            return 0
        # Git combines these patterns with OR and emits each commit once.
        return len({line.strip() for line in bug_log_result.stdout.splitlines() if line.strip()})
    except OSError:
        return 0


_NON_CODE_EXTENSIONS = (".md", ".txt", ".json", ".yaml", ".yml", ".lock")


def _resolve_target_files(repo_path: Path, files: list[str] | None) -> list[str]:
    """Return ``files`` or fall back to ``git ls-files`` output."""
    if files is not None:
        return files
    try:
        ls_files_result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if ls_files_result.returncode != 0:
        return []
    return [f.strip() for f in ls_files_result.stdout.strip().split("\n") if f.strip()]


def _file_hotspot(repo_path: Path, file_path: str, since: str) -> HotspotMetrics | None:
    """Analyze a single file; returns None for non-code or untouched files."""
    if file_path.endswith(_NON_CODE_EXTENSIONS):
        return None

    file_commits, churn = _get_file_commits_with_info(repo_path, file_path, since)
    total_commits = len(file_commits)
    if total_commits == 0:
        return None

    bug_fixes = _get_bug_fix_commits(repo_path, file_path, since)

    author_counts: dict[str, int] = defaultdict(int)
    for _, author, _ in file_commits:
        author_counts[author] += 1

    author_count = len(author_counts)
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    bug_density = bug_fixes / total_commits

    # Only include if there's actual risk
    if not (bug_fixes > 0 or churn > 50 or author_count == 1):
        return None

    return HotspotMetrics(
        file_path=file_path,
        bug_fix_commits=bug_fixes,
        total_commits=total_commits,
        bug_density=round(bug_density, 2),
        code_churn_lines=churn,
        author_count=author_count,
        top_authors=top_authors,
    )


def _hotspot_risk_score(h: HotspotMetrics) -> float:
    """High bug density + high churn + low bus factor = high risk."""
    bus_factor_penalty = 2.0 if h.author_count == 1 else 1.0
    return h.bug_density * h.code_churn_lines * bus_factor_penalty


def identify_bug_hotspots(
    repo_path: Path,
    files: list[str] | None = None,
    top_n: int = 10,
    since: str = "90.days.ago",
) -> list[HotspotMetrics]:
    """Identify files with high bug-fix density and code churn.
    
    These files are risky - they break often and change frequently.
    
    Args:
        repo_path: Path to git repository
        files: Specific files to analyze (None = all tracked files)
        top_n: Return top N hotspots
        since: Time window for analysis
    
    Returns:
        List of HotspotMetrics sorted by risk score (bug_density * churn)
    """
    files = _resolve_target_files(repo_path, files)
    if not files:
        return []
    
    hotspots = [
        m for f in files
        if (m := _file_hotspot(repo_path, f, since)) is not None
    ]
    hotspots.sort(key=_hotspot_risk_score, reverse=True)
    return hotspots[:top_n]


def _get_file_authors(repo_path: Path, file_path: str) -> list[str] | None:
    """Return unique authors for a file, or None if git log fails."""
    try:
        authors_result = subprocess.run(
            ["git", "log", "--format=%an", "--", file_path],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if authors_result.returncode != 0:
        return None
    return sorted({line.strip() for line in authors_result.stdout.strip().split("\n") if line.strip()})


def calculate_bus_factor(
    repo_path: Path,
    files: list[str] | None = None,
    critical_threshold: int = 2,  # Files with bus factor <= this are critical
) -> dict[str, int]:
    """Calculate bus factor (number of unique authors) per file.
    
    Bus factor = 1 means only 1 person knows this code - high risk!
    Bus factor >= 3 is healthy.
    
    Returns:
        Dict of {file_path: author_count}
        Only includes files with bus_factor <= critical_threshold
    """
    target_files = _resolve_target_files(repo_path, files)
    if not target_files:
        return {}
    
    bus_factors: dict[str, int] = {}
    for file_path in target_files:
        if file_path.endswith(_NON_CODE_EXTENSIONS):
            continue
        authors = _get_file_authors(repo_path, file_path)
        if authors is None:
            continue
        author_count = len(authors)
        if author_count <= critical_threshold:
            bus_factors[file_path] = author_count
    
    return bus_factors


def get_critical_bus_factor_files(
    repo_path: Path,
    bus_factors: dict[str, int] | None = None,
) -> list[tuple[str, int, list[str]]]:
    """Get files with critical bus factor (1-2 authors) + their authors.
    
    Returns:
        [(file_path, author_count, [author_names]), ...]
    """
    if bus_factors is None:
        bus_factors = calculate_bus_factor(repo_path, critical_threshold=2)
    
    critical: list[tuple[str, int, list[str]]] = []
    for file_path, author_count in bus_factors.items():
        authors = _get_file_authors(repo_path, file_path)
        if authors is not None:
            critical.append((file_path, author_count, authors))
    
    # Sort by author_count asc, then by path
    critical.sort(key=lambda x: (x[1], x[0]))
    return critical

