from pathlib import Path

from nxdo.text_builder import LineBuilder


def _is_visible(path: Path) -> bool:
    return not path.name.startswith(".")


def _visible_children(root: Path) -> list[Path]:
    try:
        children = [p for p in root.iterdir() if _is_visible(p)]
        return sorted(children, key=lambda p: p.name)
    except OSError:
        return []


def _format_node(entry: Path, is_last: bool, prefix: str) -> tuple[str, str]:
    connector = "└── " if is_last else "├── "
    extension = "    " if is_last else "│   "
    return f"{prefix}{connector}{entry.name}", f"{prefix}{extension}"


def _entry_lines(
    child: Path,
    is_last: bool,
    prefix: str,
    depth: int,
    max_depth: int,
) -> list[str]:
    line, child_prefix = _format_node(child, is_last, prefix)
    if child.is_dir() and depth + 1 < max_depth:
        return [line, *_collect_tree_lines(child, max_depth, depth + 1, child_prefix)]
    return [line]


def _collect_tree_lines(
    root: Path,
    max_depth: int,
    depth: int = 0,
    prefix: str = "",
) -> list[str]:
    if depth >= max_depth or not root.is_dir():
        return []

    children = _visible_children(root)
    last_idx = len(children) - 1
    return [
        line
        for idx, child in enumerate(children)
        for line in _entry_lines(child, idx == last_idx, prefix, depth, max_depth)
    ]


def _build_tree(root: Path, max_depth: int, depth: int = 0, prefix: str = "") -> str:
    """Build ASCII tree representation of directory structure."""
    return LineBuilder(*_collect_tree_lines(root, max_depth, depth, prefix)).text()
