"""Shared helper for assembling multi-line text output."""

from __future__ import annotations


class LineBuilder:
    """Single owner of the line-list mutation used to assemble text blocks."""

    def __init__(self, *initial: str) -> None:
        self._lines = list(initial)

    def line(self, *lines: str) -> None:
        """Append one or more lines."""
        self._lines.extend(lines)

    def text(self) -> str:
        """Return the accumulated lines joined with newlines."""
        return "\n".join(self._lines)
