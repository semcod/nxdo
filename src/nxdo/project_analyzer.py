"""Collect static project metadata for the LLM prompt."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


SNAPSHOT_FILES = [
    "README.md",
    "README.rst",
    "README.txt",
    "CHANGELOG.md",
    "CHANGELOG.rst",
    "TODO.md",
    "ROADMAP.md",
    "ROADMAP.rst",
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "package.json",
    "Cargo.toml",
    "go.mod",
]

MAX_FILE_CHARS = 3_000
MAX_TREE_DEPTH = 3
IGNORED_TREE_NAMES = {
    ".code2llm_cache",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
IGNORED_TREE_SUFFIXES = {
    ".gif",
    ".jpg",
    ".jpeg",
    ".lock",
    ".png",
    ".pyc",
    ".webp",
}


@dataclass
class ProjectSnapshot:
    root: Path
    name: str
    description: str
    language_stack: list[str]
    file_contents: dict[str, str] = field(default_factory=dict)
    directory_tree: str = ""
    extras: dict[str, str] = field(default_factory=dict)

    def to_text(self) -> str:
        lines = [
            f"Project: {self.name}",
            f"Description: {self.description or 'n/a'}",
            f"Stack: {', '.join(self.language_stack) or 'unknown'}",
            "",
        ]
        for file_name, content in self.file_contents.items():
            lines += [f"--- {file_name} ---", content, ""]
        if self.directory_tree:
            lines += ["--- Directory tree ---", self.directory_tree, ""]
        return "\n".join(lines)


def _read_file_safely(path: Path) -> str | None:
    """Read file content safely, return None on error."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _truncate_file_content(text: str) -> str:
    """Truncate file content with truncation message if needed."""
    if len(text) > MAX_FILE_CHARS:
        return text[:MAX_FILE_CHARS] + f"\n... [truncated, {len(text)} chars total]"
    return text


def _collect_file_contents(root: Path) -> dict[str, str]:
    """Collect contents of snapshot files with truncation."""
    file_contents: dict[str, str] = {}
    for rel_path in SNAPSHOT_FILES:
        path = root / rel_path
        if not path.exists():
            continue
        text = _read_file_safely(path)
        if text is None:
            continue
        file_contents[rel_path] = _truncate_file_content(text)
    return file_contents


def _resolve_name_and_description(root: Path, file_contents: dict[str, str], default_name: str) -> tuple[str, str]:
    """Resolve project name and description from manifest files."""
    name = default_name
    description = ""

    manifest_parsers = [
        ("pyproject.toml", lambda: _parse_pyproject(file_contents["pyproject.toml"], name)),
        ("package.json", lambda: _parse_package_json(root / "package.json", name)),
        ("Cargo.toml", lambda: _parse_cargo(file_contents["Cargo.toml"], name)),
        ("README.md", lambda: (name, _readme_summary(file_contents["README.md"]))),
    ]

    for filename, parser in manifest_parsers:
        if filename in file_contents:
            name, description = parser()
            break

    return name, description


def analyze_project(root: Path) -> ProjectSnapshot:
    name = root.name
    file_contents = _collect_file_contents(root)
    stack = _detect_stack(root)
    name, description = _resolve_name_and_description(root, file_contents, name)

    return ProjectSnapshot(
        root=root,
        name=name,
        description=description,
        language_stack=stack,
        file_contents=file_contents,
        directory_tree=_build_tree(root, MAX_TREE_DEPTH),
    )


def _check_pattern_match(root: Path, pattern: str) -> bool:
    """Check if a pattern matches in the root directory."""
    if "*" in pattern:
        return next(root.rglob(pattern), None) is not None
    else:
        return (root / pattern).exists()


def _detect_stack(root: Path) -> list[str]:
    markers = {
        "Python": ["pyproject.toml", "setup.py", "requirements.txt", "*.py"],
        "JavaScript/TypeScript": ["package.json", "tsconfig.json"],
        "Rust": ["Cargo.toml"],
        "Go": ["go.mod"],
        "Java": ["pom.xml", "build.gradle"],
        "Docker": ["Dockerfile", "docker-compose.yml"],
        "Terraform": ["*.tf"],
    }
    found: list[str] = []
    for stack_name, patterns in markers.items():
        if any(_check_pattern_match(root, pattern) for pattern in patterns):
            found.append(stack_name)
    return found


def _parse_pyproject_tomllib(text: str, fallback: str) -> tuple[str, str] | None:
    """Parse pyproject.toml using tomllib if available."""
    if tomllib is None:
        return None
    try:
        parsed = tomllib.loads(text)
    except ValueError:
        return None
    project = parsed.get("project", {})
    if isinstance(project, dict):
        return project.get("name", fallback), project.get("description", "")
    return None


def _parse_pyproject_regex(text: str, fallback: str) -> tuple[str, str]:
    """Parse pyproject.toml using regex fallback."""
    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    description_match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return (
        name_match.group(1) if name_match else fallback,
        description_match.group(1) if description_match else "",
    )


def _parse_pyproject(text: str, fallback: str) -> tuple[str, str]:
    tomllib_result = _parse_pyproject_tomllib(text, fallback)
    if tomllib_result is not None:
        return tomllib_result
    return _parse_pyproject_regex(text, fallback)


def _parse_package_json(path: Path, fallback: str) -> tuple[str, str]:
    try:
        package_json = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return fallback, ""
    return package_json.get("name", fallback), package_json.get("description", "")


def _parse_cargo(text: str, fallback: str) -> tuple[str, str]:
    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    description_match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return (
        name_match.group(1) if name_match else fallback,
        description_match.group(1) if description_match else "",
    )


def _readme_summary(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def _should_ignore_entry(name: str) -> bool:
    """Check if a directory/file should be ignored in tree view."""
    path = Path(name)
    return (
        name in IGNORED_TREE_NAMES
        or name.startswith(".")
        or name.endswith(".egg-info")
        or path.suffix.lower() in IGNORED_TREE_SUFFIXES
    )


def _get_tree_symbol(is_last: bool, connector: bool) -> str:
    """Get tree symbol for connector or extension."""
    if connector:
        return "└── " if is_last else "├── "
    else:
        return "    " if is_last else "│   "


def _get_connector(is_last: bool) -> str:
    """Get the tree connector symbol."""
    return _get_tree_symbol(is_last, connector=True)


def _get_extension(is_last: bool) -> str:
    """Get the tree extension for nested levels."""
    return _get_tree_symbol(is_last, connector=False)


def _build_tree(root: Path, max_depth: int, depth: int = 0, prefix: str = "") -> str:
    """Build ASCII tree representation of directory structure."""
    lines: list[str] = []
    stack: list[tuple[str, Path, int, str]] = []

    def push_children(directory: Path, node_depth: int, node_prefix: str) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda entry: (entry.is_file(), entry.name.lower()))
        except OSError:
            return
        visible_entries = [entry for entry in entries if not _should_ignore_entry(entry.name)]
        last_index = len(visible_entries) - 1
        for index in range(last_index, -1, -1):
            entry = visible_entries[index]
            is_last = index == last_index
            item = (
                node_prefix + _get_connector(is_last) + entry.name,
                entry,
                node_depth,
                node_prefix + _get_extension(is_last),
            )
            stack.append(item)

    push_children(root, depth, prefix)
    while stack:
        line, entry, node_depth, entry_prefix = stack.pop()
        lines.append(line)
        if entry.is_dir() and node_depth < max_depth - 1:
            push_children(entry, node_depth + 1, entry_prefix)

    return "\n".join(lines)
