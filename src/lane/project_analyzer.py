"""Collect static project metadata for the LLM prompt."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re

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


def analyze_project(root: Path) -> ProjectSnapshot:
    name = root.name
    description = ""
    file_contents: dict[str, str] = {}

    for rel_path in SNAPSHOT_FILES:
        path = root / rel_path
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        file_contents[rel_path] = text[:MAX_FILE_CHARS]
        if len(text) > MAX_FILE_CHARS:
            file_contents[rel_path] += f"\n... [truncated, {len(text)} chars total]"

    stack = _detect_stack(root)

    if "pyproject.toml" in file_contents:
        name, description = _parse_pyproject(file_contents["pyproject.toml"], name)
    elif "package.json" in file_contents:
        name, description = _parse_package_json(root / "package.json", name)
    elif "Cargo.toml" in file_contents:
        name, description = _parse_cargo(file_contents["Cargo.toml"], name)
    elif "README.md" in file_contents:
        description = _readme_summary(file_contents["README.md"])

    return ProjectSnapshot(
        root=root,
        name=name,
        description=description,
        language_stack=stack,
        file_contents=file_contents,
        directory_tree=_build_tree(root, MAX_TREE_DEPTH),
    )


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
        for pattern in patterns:
            if "*" in pattern:
                if next(root.rglob(pattern), None):
                    found.append(stack_name)
                    break
            elif (root / pattern).exists():
                found.append(stack_name)
                break
    return found


def _parse_pyproject(text: str, fallback: str) -> tuple[str, str]:
    if tomllib is not None:
        try:
            parsed = tomllib.loads(text)
        except Exception:
            parsed = {}
        project = parsed.get("project", {})
        if isinstance(project, dict):
            return project.get("name", fallback), project.get("description", "")

    name_match = re.search(r'^name\s*=\s*"([^"]+)"', text, re.MULTILINE)
    description_match = re.search(r'^description\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return (
        name_match.group(1) if name_match else fallback,
        description_match.group(1) if description_match else "",
    )


def _parse_package_json(path: Path, fallback: str) -> tuple[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback, ""
    return data.get("name", fallback), data.get("description", "")


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


def _build_tree(root: Path, max_depth: int, depth: int = 0, prefix: str = "") -> str:
    ignore = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
    }
    try:
        entries = sorted(root.iterdir(), key=lambda entry: (entry.is_file(), entry.name.lower()))
    except OSError:
        return ""

    visible_entries = [entry for entry in entries if entry.name not in ignore and not entry.name.startswith(".")]
    lines: list[str] = []
    for index, entry in enumerate(visible_entries):
        connector = "└── " if index == len(visible_entries) - 1 else "├── "
        lines.append(prefix + connector + entry.name)
        if entry.is_dir() and depth < max_depth - 1:
            extension = "    " if index == len(visible_entries) - 1 else "│   "
            subtree = _build_tree(entry, max_depth, depth + 1, prefix + extension)
            if subtree:
                lines.append(subtree)
    return "\n".join(lines)

