def _build_tree(root: Path, max_depth: int, depth: int = 0, prefix: str = "") -> str:
    """Build ASCII tree representation of directory structure."""
    lines = _collect_tree_lines(root, max_depth, depth, prefix)
    return LineBuilder(*lines).text()
