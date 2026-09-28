from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re

try:
    import tomllib
except ImportError:
    tomllib = None  # type: ignore[assignment]

MAX_FILE_CHARS = 3000

KEY_FILES = (
    "README.md",
    "README",
    "README.rst",
    "README.txt",
    "CHANGELOG.md",
    "CHANGELOG",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
)


@dataclass
class ProjectSnapshot:
    name: str
    description: str
    language_stack: list[str] = field(default_factory=list)
    file_contents: dict[str, str] = field(default_factory=dict)
    directory_tree: str = ""
    root_path: Path = field(default_factory=lambda: Path("."))

    @property
    def root(self) -> Path:
        return self.root_path

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "language_stack": list(self.language_stack),
            "file_contents": dict(self.file_contents),
            "directory_tree": self.directory_tree,
            "root_path": str(self.root_path),
        }


def _readme_summary(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        return line
    return ""


def _parse_pyproject_tomllib(text: str, fallback: str) -> tuple[str, str] | None:
    if tomllib is None:
        return None
    try:
        data = tomllib.loads(text)
    except (ValueError, TypeError, AttributeError):
        return None
    project = data.get("project")
    if not isinstance(project, dict):
        return None
    name = str(project.get("name", fallback))
    desc = str(project.get("description", ""))
    return name, desc


def _parse_pyproject(text: str, fallback: str) -> tuple[str, str]:
    result = _parse_pyproject_tomllib(text, fallback)
    if result is not None:
        return result
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    name = name_match.group(1) if name_match else fallback
    desc = desc_match.group(1) if desc_match else ""
    return name, desc


def _parse_package_json(pkg_file: Path, fallback: str) -> tuple[str, str]:
    try:
        data = json.loads(pkg_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return fallback, ""
        name = str(data.get("name", fallback))
        desc = str(data.get("description", ""))
        return name, desc
    except (OSError, json.JSONDecodeError, ValueError):
        return fallback, ""


def _parse_cargo(text: str, fallback: str) -> tuple[str, str]:
    if tomllib is not None:
        try:
            data = tomllib.loads(text)
            pkg = data.get("package", data)
            if isinstance(pkg, dict):
                name = str(pkg.get("name", fallback))
                desc = str(pkg.get("description", ""))
                return name, desc
        except (ValueError, TypeError, AttributeError):
            pass
    name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', text)
    desc_match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', text)
    name = name_match.group(1) if name_match else fallback
    desc = desc_match.group(1) if desc_match else ""
    return name, desc


def _detect_stack(root: Path) -> list[str]:
    stack: list[str] = []
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists() or (root / "requirements.txt").exists():
        stack.append("Python")
    if (root / "package.json").exists() or (root / "tsconfig.json").exists():
        stack.append("JavaScript/TypeScript")
    if (root / "Cargo.toml").exists():
        stack.append("Rust")
    if (root / "go.mod").exists():
        stack.append("Go")

    has_py = "Python" in stack
    has_js = "JavaScript/TypeScript" in stack
    has_rust = "Rust" in stack
    has_go = "Go" in stack

    if not (has_py and has_js and has_rust and has_go):
        try:
            for p in root.rglob("*"):
                if _should_ignore_entry(p.name) or any(part.startswith(".") for part in p.parts):
                    continue
                if not has_py and p.suffix == ".py":
                    stack.append("Python")
                    has_py = True
                elif not has_js and p.suffix in {".js", ".ts", ".jsx", ".tsx"}:
                    stack.append("JavaScript/TypeScript")
                    has_js = True
                elif not has_rust and p.suffix == ".rs":
                    stack.append("Rust")
                    has_rust = True
                elif not has_go and p.suffix == ".go":
                    stack.append("Go")
                    has_go = True
                if has_py and has_js and has_rust and has_go:
                    break
        except OSError:
            pass

    return stack


def _should_ignore_entry(name: str) -> bool:
    if name.startswith("."):
        return True
    if name.endswith(".egg-info") or name.endswith(".lock"):
        return True
    if name in {
        "node_modules",
        "__pycache__",
        "uv.lock",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "poetry.lock",
    }:
        return True
    suffix = Path(name).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pyc", ".pyo"}:
        return True
    return False


def _visible_children(path: Path) -> list[Path]:
    try:
        entries = list(path.iterdir())
    except OSError:
        return []
    visible = [e for e in entries if not _should_ignore_entry(e.name)]
    dirs = sorted([e for e in visible if e.is_dir()], key=lambda p: p.name)
    files = sorted([e for e in visible if not e.is_dir()], key=lambda p: p.name)
    return dirs + files


def _lines_for_child(
    child: Path,
    is_last: bool,
    max_depth: int,
    current_depth: int,
    prefix: str,
) -> list[str]:
    connector = "└── " if is_last else "├── "
    display_name = f"{child.name}/" if child.is_dir() else child.name
    child_line = f"{prefix}{connector}{display_name}"
    if not child.is_dir() or current_depth >= max_depth:
        return [child_line]
    indent = "    " if is_last else "│   "
    sub_lines = _collect_tree_lines(
        child,
        max_depth=max_depth,
        current_depth=current_depth + 1,
        prefix=f"{prefix}{indent}",
    )
    return [child_line, *sub_lines]


def _collect_tree_lines(
    path: Path,
    max_depth: int = 3,
    current_depth: int = 1,
    prefix: str = "",
) -> list[str]:
    if current_depth > max_depth:
        return []
    children = _visible_children(path)
    last_idx = len(children) - 1
    return [
        line
        for i, child in enumerate(children)
        for line in _lines_for_child(
            child,
            is_last=(i == last_idx),
            max_depth=max_depth,
            current_depth=current_depth,
            prefix=prefix,
        )
    ]


def _get_tree_lines(root: Path, max_depth: int = 3) -> list[str]:
    try:
        if not root.is_dir():
            return []
        return _collect_tree_lines(root, max_depth=max_depth)
    except OSError:
        return []


def _build_tree(root: Path, max_depth: int = 3) -> str:
    return "\n".join(_get_tree_lines(root, max_depth=max_depth))


def analyze_project(root: Path | str = ".") -> ProjectSnapshot:
    root_path = Path(root)
    name = root_path.name or root_path.resolve().name or "project"
    description = ""

    pyproject_path = root_path / "pyproject.toml"
    package_json_path = root_path / "package.json"
    cargo_path = root_path / "Cargo.toml"

    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text(encoding="utf-8")
            name, description = _parse_pyproject(content, name)
        except OSError:
            pass
    elif package_json_path.exists():
        try:
            name, description = _parse_package_json(package_json_path, name)
        except OSError:
            pass
    elif cargo_path.exists():
        try:
            content = cargo_path.read_text(encoding="utf-8")
            name, description = _parse_cargo(content, name)
        except OSError:
            pass

    if not description:
        for readme_name in ("README.md", "README", "README.rst", "README.txt"):
            readme_file = root_path / readme_name
            if readme_file.exists():
                try:
                    summary = _readme_summary(readme_file.read_text(encoding="utf-8"))
                    if summary:
                        description = summary
                        break
                except OSError:
                    pass

    file_contents: dict[str, str] = {}
    try:
        entries = sorted(root_path.iterdir(), key=lambda p: p.name)
        for entry in entries:
            if entry.is_file() and (entry.name in KEY_FILES or entry.suffix.lower() in {".md", ".rst", ".txt"}):
                try:
                    text = entry.read_text(encoding="utf-8", errors="replace")
                    if len(text) > MAX_FILE_CHARS:
                        text = text[:MAX_FILE_CHARS] + "\n... [truncated]"
                    file_contents[entry.name] = text
                except OSError:
                    pass
    except OSError:
        pass

    language_stack = _detect_stack(root_path)
    directory_tree = _build_tree(root_path)

    return ProjectSnapshot(
        name=name,
        description=description,
        language_stack=language_stack,
        file_contents=file_contents,
        directory_tree=directory_tree,
        root_path=root_path,
    )
