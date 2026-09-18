"""Change coupling analysis - which files change together frequently."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import subprocess


@dataclass
class CouplingMetrics:
    """Metrics for file pair coupling."""
    file_a: str
    file_b: str
    coupling_score: float  # 0.0 - 1.0, how often they change together
    commits_together: int
    total_commits_a: int
    total_commits_b: int


def _get_commits_with_files(repo_path: Path, max_commits: int = 100) -> list[list[str]]:
    """Get list of commits with their changed files.
    
    Returns: List of [file1, file2, ...] for each commit
    """
    try:
        log_result = subprocess.run(
            ["git", "log", f"-{max_commits}", "--name-only", "--pretty=format:%H"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if log_result.returncode != 0:
            return []

        commits = []
        current_files: list[str] = []

        for line in log_result.stdout.strip().split("\n"):
            if not line:
                if current_files:
                    commits.append(current_files)
                    current_files = []
            elif len(line) == 40 and all(c in "0123456789abcdef" for c in line.lower()):
                # This is a commit hash, skip it
                if current_files:
                    commits.append(current_files)
                    current_files = []
            else:
                # This is a file path
                if line.strip() and not line.startswith("commit "):
                    current_files.append(line.strip())
        
        if current_files:
            commits.append(current_files)
        
        return commits
    except Exception:
        return []


def _filtered_commit_files(
    commit_files: list[str],
    file_filter: set[str] | None,
) -> list[str]:
    """Keep only files matching ``file_filter`` extensions and drop
    binary/test/generated paths."""
    filtered = commit_files
    if file_filter:
        filtered = [f for f in filtered if any(f.endswith(ext) for ext in file_filter)]
    return [
        f for f in filtered
        if not any(x in f for x in ["test", "__pycache__", ".pyc", ".min.", "dist/", "build/"])
    ]


def _score_file_pairs(
    file_commits: dict[str, int],
    file_pair_commits: dict[tuple[str, str], int],
    min_coupling: float,
) -> list[CouplingMetrics]:
    """Score co-changing file pairs: commits_together / min(total_a, total_b)."""
    results: list[CouplingMetrics] = []
    for (file_a, file_b), together in file_pair_commits.items():
        total_a = file_commits[file_a]
        total_b = file_commits[file_b]
        if total_a <= 0 or total_b <= 0:
            continue
        coupling = together / min(total_a, total_b)
        if coupling < min_coupling:
            continue
        results.append(CouplingMetrics(
            file_a=file_a,
            file_b=file_b,
            coupling_score=round(coupling, 2),
            commits_together=together,
            total_commits_a=total_a,
            total_commits_b=total_b,
        ))
    return results


def collect_coupling_matrix(
    repo_path: Path,
    max_commits: int = 100,
    min_coupling: float = 0.3,
    file_filter: set[str] | None = None,
) -> list[CouplingMetrics]:
    """Analyze which files change together frequently.
    
    Args:
        repo_path: Path to git repository
        max_commits: How many recent commits to analyze
        min_coupling: Minimum coupling score to include (0.0 - 1.0)
        file_filter: Only include files with these extensions (e.g., {'.py', '.js'})
    
    Returns:
        List of CouplingMetrics sorted by coupling_score desc
    
    Example:
        >>> metrics = collect_coupling_matrix(Path("."), min_coupling=0.5)
        >>> for m in metrics[:5]:
        ...     print(f"{m.file_a} <-> {m.file_b}: {m.coupling_score:.2f}")
    """
    commit_file_groups = _get_commits_with_files(repo_path, max_commits)
    if not commit_file_groups:
        return []

    # Count file occurrences and co-occurrences
    file_commits: dict[str, int] = defaultdict(int)
    file_pair_commits: dict[tuple[str, str], int] = defaultdict(int)

    for commit_files in commit_file_groups:
        filtered = _filtered_commit_files(commit_files, file_filter)
        for f in filtered:
            file_commits[f] += 1
        for i, f1 in enumerate(filtered):
            for f2 in filtered[i+1:]:
                pair = (f1, f2) if f1 < f2 else (f2, f1)
                file_pair_commits[pair] += 1
    
    # Calculate coupling scores
    results = _score_file_pairs(file_commits, file_pair_commits, min_coupling)
    results.sort(key=lambda x: x.coupling_score, reverse=True)
    return results


def get_coupling_clusters(
    coupling_metrics: list[CouplingMetrics],
    min_coupling: float = 0.5,
) -> list[set[str]]:
    """Group files into clusters based on high coupling.
    
    Files in same cluster should be refactored together in same sprint.
    
    Uses simple connected components algorithm.
    """
    from collections import deque
    
    # Build adjacency list for high-coupling pairs
    graph: dict[str, set[str]] = defaultdict(set)
    
    for m in coupling_metrics:
        if m.coupling_score >= min_coupling:
            graph[m.file_a].add(m.file_b)
            graph[m.file_b].add(m.file_a)
    
    # Find connected components (clusters)
    visited: set[str] = set()
    clusters: list[set[str]] = []
    
    for start_node in graph:
        if start_node in visited:
            continue
        
        # BFS to find all connected nodes
        cluster: set[str] = set()
        queue = deque([start_node])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            cluster.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
        
        if len(cluster) > 1:  # Only clusters with 2+ files
            clusters.append(cluster)
    
    # Sort by cluster size (largest first)
    clusters.sort(key=len, reverse=True)
    
    return clusters
