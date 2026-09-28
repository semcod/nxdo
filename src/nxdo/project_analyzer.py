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


def _collect_tree_lines(
    root: Path,
    max_depth: int,
    depth: int = 0,
    prefix: str = "",
) -> list[str]:
    if depth >= max_depth or not root.is_dir():
        return []

    lines: list[str] = []
    children = _visible_children(root)
    total = len(children)

    for index, child in enumerate(children):
        is_last = index == total - 1
        line, child_prefix = _format_node(child, is_last, prefix)
        lines.append(line)
        if child.is_dir() and depth + 1 < max_depth:
            sublines = _collect_tree_lines(child, max_depth, depth + 1, child_prefix)
            lines.extend(sublines)

    return lines


def _build_tree(root: Path, max_depth: int, depth: int = 0, prefix: str = "") -> str:
    """Build ASCII tree representation of directory structure."""
    lines = _collect_tree_lines(root, max_depth, depth, prefix)
    return LineBuilder(*lines).text()
