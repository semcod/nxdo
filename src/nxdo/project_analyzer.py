from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

MAX_FILE_CHARS = 3000

KEY_FILES: tuple[str, ...] = (
    "README.md",
    "README.rst",
    "README.txt",
    "README",
    "CHANGELOG.md",
    "CHANGELOG.rst",
    "CHANGELOG.txt",
    "CHANGELOG",
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
)

_IGNORE_SUFFIXES: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".lock", ".pyc"}
)
_IGNORE_NAMES: frozenset[str] = frozenset(
    {"__pycache__", "uv.lock", "node_modules", ".git"}
)


@dataclass
class ProjectSnapshot:
    name: str
    description: str = ""
    language_stack: list[str] = field(default_factory=list)
    file_contents: dict[str, str] = field(default_factory=dict)
    directory_tree: str = ""

    def to_text(self) -> str:
        parts: list[str] = [f"Project: {self.name}"]
        if self.description:
            parts.append(f"Description: {self.description}")
        if self.language_stack:
            parts.append(f"Stack: {', '.join(self.language_stack)}")
        if self.directory_tree:
            parts.append(f"\nDirectory Tree:\n{self.directory_tree}")
        if self.file_contents:
            parts.append("\nKey Files:")
            for fname, content in sorted(self.file_contents.items()):
                parts.append(f"--- {fname} ---\n{content}")
        return "\n".join(parts)

    def __str__(self) -> str:
        return self.to_text()


def _read_file_content(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > MAX_FILE_CHARS:
            return content[:MAX_FILE_CHARS] + "\n... [truncated]"
        return content
    except OSError:
        return None


def _readme_summary(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped
    return ""


def _parse_pyproject_tomllib(text: str, fallback_name: str) -> tuple[str, str] | None:
    if tomllib is None:
        return None
    try:
        data = tomllib.loads(text)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    name = project.get("name") or fallback_name
    description = project.get("description") or ""
    return str(name), str(description)


def _parse_pyproject(text: str, fallback_name: str) -> tuple[str, str]:
    parsed = _parse_pyproject_tomllib(text, fallback_name)
    if parsed is not None:
        return parsed
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    name = name_match.group(1) if name_match else fallback_name
    desc = desc_match.group(1) if desc_match else ""
    return name, desc


def _parse_package_json(pkg_file: Path, fallback_name: str) -> tuple[str, str]:
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            name = data.get("name") or fallback_name
            desc = data.get("description") or ""
            return str(name), str(desc)
    except (ValueError, TypeError, OSError):
        return fallback_name, ""
    return fallback_name, ""


def _parse_cargo(text: str, fallback_name: str) -> tuple[str, str]:
    if tomllib is not None:
        try:
            data = tomllib.loads(text)
            if isinstance(data, dict):
                pkg = data.get("package", data)
                if isinstance(pkg, dict):
                    name = pkg.get("name") or fallback_name
                    desc = pkg.get("description") or ""
                    return str(name), str(desc)
        except (ValueError, TypeError):
            data = None
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    name = name_match.group(1) if name_match else fallback_name
    desc = desc_match.group(1) if desc_match else ""
    return name, desc


def _detect_stack(root: Path) -> list[str]:
    stack: list[str] = []

    def _add(lang: str) -> None:
        if lang not in stack:
            stack.append(lang)

    if (
        (root / "pyproject.toml").is_file()
        or (root / "setup.py").is_file()
        or (root / "requirements.txt").is_file()
    ):
        _add("Python")
    if (root / "package.json").is_file() or (root / "tsconfig.json").is_file():
        _add("JavaScript/TypeScript")
    if (root / "Cargo.toml").is_file():
        _add("Rust")
    if (root / "go.mod").is_file():
        _add("Go")

    try:
        entries = list(root.rglob("*"))
    except OSError:
        entries = []

    for path in entries:
        if _should_ignore_entry(path.name):
            continue
        if path.is_file():
            suffix = path.suffix.lower()
            if suffix == ".py":
                _add("Python")
            elif suffix in {".js", ".ts", ".jsx", ".tsx"}:
                _add("JavaScript/TypeScript")
            elif suffix == ".rs":
                _add("Rust")
            elif suffix == ".go":
                _add("Go")

    return stack


def _should_ignore_entry(name: str) -> bool:
    if name.startswith(".") or name.endswith(".egg-info"):
        return True
    if name in _IGNORE_NAMES:
        return True
    return Path(name).suffix.lower() in _IGNORE_SUFFIXES


def _visible_children(directory: Path) -> list[Path]:
    try:
        entries = [
            p for p in directory.iterdir() if not _should_ignore_entry(p.name)
        ]
    except OSError:
        return []
    dirs = sorted([p for p in entries if p.is_dir()], key=lambda p: p.name)
    files = sorted([p for p in entries if not p.is_dir()], key=lambda p: p.name)
    return dirs + files


def _collect_tree_lines(
    root: Path,
    max_depth: int = 3,
    current_depth: int = 1,
    prefix: str = "",
) -> list[str]:
    if current_depth > max_depth:
        return []
    lines: list[str] = []
    for child in _visible_children(root):
        display_name = f"{prefix}{child.name}{'/' if child.is_dir() else ''}"
        lines.append(display_name)
        if child.is_dir() and current_depth < max_depth:
            sub_lines = _collect_tree_lines(
                child,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                prefix=f"{prefix}  ",
            )
            lines.extend(sub_lines)
    return lines


def _build_tree(root: Path, max_depth: int = 3) -> str:
    try:
        lines = _collect_tree_lines(root, max_depth=max_depth)
        return "\n".join(lines)
    except OSError:
        return ""


def analyze_project(root: Path) -> ProjectSnapshot:
    name = root.name
    desc = ""

    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file():
        try:
            text = pyproject_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        if text:
            name, desc = _parse_pyproject(text, name)

    package_json_path = root / "package.json"
    if package_json_path.is_file() and name == root.name:
        try:
            name, desc = _parse_package_json(package_json_path, name)
        except OSError:
            name, desc = root.name, ""

    cargo_path = root / "Cargo.toml"
    if cargo_path.is_file() and name == root.name:
        try:
            text = cargo_path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        if text:
            name, desc = _parse_cargo(text, name)

    if not desc:
        for readme_name in ("README.md", "README.rst", "README.txt", "README"):
            readme_path = root / readme_name
            if readme_path.is_file():
                try:
                    text = readme_path.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    summary = _readme_summary(text)
                except OSError:
                    summary = ""
                if summary:
                    desc = summary
                    break

    file_contents: dict[str, str] = {}
    for fname in KEY_FILES:
        fpath = root / fname
        if fpath.is_file():
            content = _read_file_content(fpath)
            if content is not None:
                file_contents[fname] = content

    stack = _detect_stack(root)
    tree = _build_tree(root)

    return ProjectSnapshot(
        name=name,
        description=desc,
        language_stack=stack,
        file_contents=file_contents,
        directory_tree=tree,
    )
