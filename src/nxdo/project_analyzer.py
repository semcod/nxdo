from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment]

MAX_FILE_CHARS: int = 3000


@dataclass
class ProjectSnapshot:
    name: str
    description: str
    language_stack: list[str] = field(default_factory=list)
    file_contents: dict[str, str] = field(default_factory=dict)
    directory_tree: str = ""


def _parse_pyproject_tomllib(text: str, fallback_name: str) -> tuple[str, str] | None:
    if tomllib is None:
        return None
    try:
        data = tomllib.loads(text)
    except (ValueError, TypeError):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    name = project.get("name", fallback_name)
    description = project.get("description", "")
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
            name = data.get("name", fallback_name)
            desc = data.get("description", "")
            return str(name), str(desc)
    except (ValueError, OSError):
        pass
    return fallback_name, ""


def _parse_cargo(text: str, fallback_name: str) -> tuple[str, str]:
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    name = name_match.group(1) if name_match else fallback_name
    desc = desc_match.group(1) if desc_match else ""
    return name, desc


def _readme_summary(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        return line
    return ""


def _detect_stack(root: Path) -> list[str]:
    stack: list[str] = []

    def _add(lang: str) -> None:
        if lang not in stack:
            stack.append(lang)

    if (root / "pyproject.toml").is_file() or (root / "setup.py").is_file() or (root / "requirements.txt").is_file():
        _add("Python")
    if (root / "package.json").is_file() or (root / "tsconfig.json").is_file():
        _add("JavaScript/TypeScript")
    if (root / "Cargo.toml").is_file():
        _add("Rust")
    if (root / "go.mod").is_file():
        _add("Go")

    try:
        for _, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not _should_ignore_entry(d)]
            for filename in filenames:
                if _should_ignore_entry(filename):
                    continue
                ext = Path(filename).suffix.lower()
                if ext == ".py":
                    _add("Python")
                elif ext in {".js", ".ts", ".jsx", ".tsx"}:
                    _add("JavaScript/TypeScript")
                elif ext == ".rs":
                    _add("Rust")
                elif ext == ".go":
                    _add("Go")
    except OSError:
        pass

    return stack


def _should_ignore_entry(name: str) -> bool:
    if name.startswith("."):
        return True
    if name.endswith(".egg-info") or name.endswith(".lock") or name.endswith(".png"):
        return True
    if name in {"__pycache__", "node_modules"}:
        return True
    return False


def _visible_children(path: Path) -> list[Path]:
    entries = [p for p in path.iterdir() if not _should_ignore_entry(p.name)]
    return sorted(entries, key=lambda p: (not p.is_dir(), p.name))


def _format_tree_node(entry: Path, prefix: str = "") -> str:
    suffix = "/" if entry.is_dir() else ""
    return f"{prefix}{entry.name}{suffix}"


def _entry_lines(entry: Path, max_depth: int, depth: int = 1, prefix: str = "") -> list[str]:
    lines = [_format_tree_node(entry, prefix)]
    if entry.is_dir() and depth < max_depth:
        for child in _visible_children(entry):
            lines.extend(_entry_lines(child, max_depth=max_depth, depth=depth + 1, prefix=prefix + "  "))
    return lines


def _collect_tree_lines(root: Path, max_depth: int = 3) -> list[str]:
    lines: list[str] = []
    for child in _visible_children(root):
        lines.extend(_entry_lines(child, max_depth=max_depth, depth=1, prefix=""))
    return lines


def _build_tree(root: Path, max_depth: int = 3) -> str:
    try:
        return "\n".join(_collect_tree_lines(root, max_depth=max_depth))
    except OSError:
        return ""


def analyze_project(root: Path) -> ProjectSnapshot:
    name = root.name
    description = ""

    pyproject_file = root / "pyproject.toml"
    package_json = root / "package.json"
    cargo_toml = root / "Cargo.toml"

    if pyproject_file.is_file():
        try:
            content = pyproject_file.read_text(encoding="utf-8")
            p_name, p_desc = _parse_pyproject(content, name)
            if p_name:
                name = p_name
            if p_desc:
                description = p_desc
        except OSError:
            pass
    elif package_json.is_file():
        p_name, p_desc = _parse_package_json(package_json, name)
        if p_name:
            name = p_name
        if p_desc:
            description = p_desc
    elif cargo_toml.is_file():
        try:
            content = cargo_toml.read_text(encoding="utf-8")
            c_name, c_desc = _parse_cargo(content, name)
            if c_name:
                name = c_name
            if c_desc:
                description = c_desc
        except OSError:
            pass

    if not description:
        readme_file = root / "README.md"
        if not readme_file.is_file():
            readme_file = root / "README"
        if readme_file.is_file():
            try:
                readme_text = readme_file.read_text(encoding="utf-8")
                description = _readme_summary(readme_text)
            except OSError:
                pass

    language_stack = _detect_stack(root)
    directory_tree = _build_tree(root)

    file_contents: dict[str, str] = {}
    try:
        for entry in sorted(root.iterdir(), key=lambda p: p.name):
            if not entry.is_file() or _should_ignore_entry(entry.name):
                continue
            try:
                text = entry.read_text(encoding="utf-8")
                if len(text) > MAX_FILE_CHARS:
                    text = text[:MAX_FILE_CHARS] + "\n... [truncated]"
                file_contents[entry.name] = text
            except (OSError, UnicodeDecodeError):
                continue
    except OSError:
        pass

    return ProjectSnapshot(
        name=name,
        description=description,
        language_stack=language_stack,
        file_contents=file_contents,
        directory_tree=directory_tree,
    )
