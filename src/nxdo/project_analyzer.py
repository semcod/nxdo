from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment]

MAX_FILE_CHARS: int = 3000


@dataclass
class ProjectSnapshot:
    name: str
    description: str = ""
    language_stack: list[str] = field(default_factory=list)
    file_contents: dict[str, str] = field(default_factory=dict)
    directory_tree: str = ""

    def to_text(self) -> str:
        lines: list[str] = [f"Project: {self.name}"]
        if self.description:
            lines.append(f"Description: {self.description}")
        if self.language_stack:
            lines.append(f"Language stack: {', '.join(self.language_stack)}")
        if self.directory_tree:
            lines.append(f"Directory tree:\n{self.directory_tree}")
        if self.file_contents:
            lines.append("Files:")
            for fname, content in sorted(self.file_contents.items()):
                lines.append(f"--- {fname} ---\n{content}")
        return "\n\n".join(lines)


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
    return str(project.get("name", fallback_name)), str(project.get("description", ""))


def _parse_pyproject(text: str, fallback_name: str) -> tuple[str, str]:
    parsed = _parse_pyproject_tomllib(text, fallback_name)
    if parsed is not None:
        return parsed
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    return (
        name_match.group(1) if name_match else fallback_name,
        desc_match.group(1) if desc_match else "",
    )


def _parse_package_json(pkg_file: Path, fallback_name: str) -> tuple[str, str]:
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return str(data.get("name", fallback_name)), str(data.get("description", ""))
    except (ValueError, OSError):
        pass
    return fallback_name, ""


def _parse_cargo(text: str, fallback_name: str) -> tuple[str, str]:
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    return (
        name_match.group(1) if name_match else fallback_name,
        desc_match.group(1) if desc_match else "",
    )


def _readme_summary(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        return line
    return ""


_ROOT_MANIFESTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("pyproject.toml", "setup.py", "requirements.txt"), "Python"),
    (("package.json", "tsconfig.json"), "JavaScript/TypeScript"),
    (("Cargo.toml",), "Rust"),
    (("go.mod",), "Go"),
)

_EXTENSION_TO_STACK: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript/TypeScript",
    ".ts": "JavaScript/TypeScript",
    ".jsx": "JavaScript/TypeScript",
    ".tsx": "JavaScript/TypeScript",
    ".rs": "Rust",
    ".go": "Go",
}


def _detect_manifest_stack(root: Path) -> list[str]:
    stack: list[str] = []
    for filenames, lang in _ROOT_MANIFESTS:
        if any((root / fname).is_file() for fname in filenames):
            stack.append(lang)
    return stack


def _record_file_language(filename: str, stack: list[str]) -> None:
    if _should_ignore_entry(filename):
        return
    lang = _EXTENSION_TO_STACK.get(Path(filename).suffix.lower())
    if lang and lang not in stack:
        stack.append(lang)


def _walk_stack(root: Path, stack: list[str]) -> None:
    try:
        for _, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not _should_ignore_entry(d)]
            for filename in filenames:
                _record_file_language(filename, stack)
    except OSError:
        pass


def _detect_stack(root: Path) -> list[str]:
    stack = _detect_manifest_stack(root)
    _walk_stack(root, stack)
    return stack


def _should_ignore_entry(name: str) -> bool:
    if name.startswith("."):
        return True
    if name.endswith((".egg-info", ".lock", ".png")):
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


def _extract_pyproject_metadata(root: Path, fallback_name: str) -> tuple[str, str] | None:
    path = root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        name, desc = _parse_pyproject(path.read_text(encoding="utf-8"), fallback_name)
        return name or fallback_name, desc
    except OSError:
        return fallback_name, ""


def _extract_package_json_metadata(root: Path, fallback_name: str) -> tuple[str, str] | None:
    path = root / "package.json"
    if not path.is_file():
        return None
    name, desc = _parse_package_json(path, fallback_name)
    return name or fallback_name, desc


def _extract_cargo_metadata(root: Path, fallback_name: str) -> tuple[str, str] | None:
    path = root / "Cargo.toml"
    if not path.is_file():
        return None
    try:
        name, desc = _parse_cargo(path.read_text(encoding="utf-8"), fallback_name)
        return name or fallback_name, desc
    except OSError:
        return fallback_name, ""


def _extract_manifest_metadata(root: Path, fallback_name: str) -> tuple[str, str]:
    extractors = (
        _extract_pyproject_metadata,
        _extract_package_json_metadata,
        _extract_cargo_metadata,
    )
    for extractor in extractors:
        metadata = extractor(root, fallback_name)
        if metadata is not None:
            return metadata
    return fallback_name, ""


def _find_readme_description(root: Path) -> str:
    readme_file = root / "README.md"
    if not readme_file.is_file():
        readme_file = root / "README"
    if readme_file.is_file():
        try:
            readme_text = readme_file.read_text(encoding="utf-8")
            return _readme_summary(readme_text)
        except OSError:
            pass
    return ""


def _collect_file_contents(root: Path) -> dict[str, str]:
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
    return file_contents


def analyze_project(root: Path | str) -> ProjectSnapshot:
    root = Path(root)
    name, description = _extract_manifest_metadata(root, root.name)
    if not description:
        description = _find_readme_description(root)

    return ProjectSnapshot(
        name=name,
        description=description,
        language_stack=_detect_stack(root),
        file_contents=_collect_file_contents(root),
        directory_tree=_build_tree(root),
    )
