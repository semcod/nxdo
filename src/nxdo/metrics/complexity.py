"""Per-file complexity metrics including fan-in, fan-out, and import analysis."""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple


class LineCounts(NamedTuple):
    """Line tallies for a single source file."""

    lines_of_code: int
    lines_of_comments: int
    blank_lines: int


class ImportBreakdown(NamedTuple):
    """Import classification and total import count for a single source file."""

    stdlib_imports: list[str]
    third_party_imports: list[str]
    local_imports: list[str]
    fan_out: int


class TypeCoverage(NamedTuple):
    """Function annotation coverage for a single source file."""

    typed_functions: int
    total_functions: int
    type_coverage: float


@dataclass
class FileMetrics:
    """Comprehensive metrics for a source file."""

    file_path: str
    lines_of_code: int
    lines_of_comments: int
    blank_lines: int
    cyclomatic_complexity: int

    # Coupling metrics
    fan_in: int  # Number of files importing this file
    fan_out: int  # Number of imports in this file

    # Type coverage (Python-specific)
    typed_functions: int
    total_functions: int
    type_coverage: float  # Percentage

    # Import analysis
    stdlib_imports: list[str]
    third_party_imports: list[str]
    local_imports: list[str]


def _classify_line(line: str) -> str:
    """Classify a single source line as blank, comment, or code."""
    stripped = line.strip()
    if not stripped:
        return "blank"
    return "comment" if stripped.startswith("#") else "code"


def _count_lines(content: str) -> LineCounts:
    """Count LOC, comments, blank lines."""
    counts = Counter(_classify_line(line) for line in content.split("\n"))
    return LineCounts(
        lines_of_code=counts["code"],
        lines_of_comments=counts["comment"],
        blank_lines=counts["blank"],
    )


def _calculate_cyclomatic_complexity(content: str) -> int:
    """Calculate cyclomatic complexity using AST."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0

    # Count decision points
    complexity = 1  # Base complexity

    decision_nodes = (
        ast.If,
        ast.While,
        ast.For,
        ast.ExceptHandler,
        ast.With,
        ast.AsyncWith,
        ast.comprehension,  # List/dict/set comprehensions
    )

    for node in ast.walk(tree):
        if isinstance(node, decision_nodes):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # Each additional operand in bool op adds complexity
            complexity += len(node.values) - 1

    return complexity


_STDLIB_MODULES = frozenset(
    {
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "collections",
        "copy",
        "csv",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "functools",
        "glob",
        "hashlib",
        "http",
        "importlib",
        "inspect",
        "itertools",
        "json",
        "logging",
        "math",
        "multiprocessing",
        "operator",
        "os",
        "pathlib",
        "pickle",
        "random",
        "re",
        "shutil",
        "socket",
        "statistics",
        "string",
        "subprocess",
        "sys",
        "tempfile",
        "textwrap",
        "threading",
        "time",
        "typing",
        "unittest",
        "urllib",
        "uuid",
        "warnings",
        "xml",
        "zipfile",
    }
)

_IMPORT_RE = re.compile(r"^(?:import\s+([\w.]+)|from\s+([\w.]+)\s+import)")


def _iter_imported_modules(content: str) -> Iterator[str]:
    """Yield the root module name of each import statement in content."""
    for line in content.split("\n"):
        if match := _IMPORT_RE.match(line.strip()):
            yield next(group for group in match.groups() if group).split(".")[0]


def _classify_import(module: str) -> str:
    """Classify an imported root module as stdlib, local, or third_party."""
    if module in _STDLIB_MODULES:
        return "stdlib"
    if module.startswith(("nxdo", ".")):
        return "local"
    return "third_party"


def _analyze_imports(content: str, file_path: str) -> ImportBreakdown:
    """Analyze imports: stdlib, third-party, local."""
    grouped: dict[str, list[str]] = defaultdict(list)
    modules = list(_iter_imported_modules(content))
    for module in modules:
        grouped[_classify_import(module)].append(module)
    return ImportBreakdown(
        stdlib_imports=grouped["stdlib"],
        third_party_imports=grouped["third_party"],
        local_imports=grouped["local"],
        fan_out=len(modules),
    )


def _has_annotated_args(args: ast.arguments) -> bool:
    """Check whether any argument (positional, keyword-only, vararg, kwarg) is annotated."""
    arg_nodes = [*args.args, *args.kwonlyargs]
    if args.vararg is not None:
        arg_nodes.append(args.vararg)
    if args.kwarg is not None:
        arg_nodes.append(args.kwarg)
    return any(arg.annotation is not None for arg in arg_nodes)


def _function_has_annotations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check whether a function has a return or argument type annotation."""
    return node.returns is not None or _has_annotated_args(node.args)


def _analyze_types(content: str) -> TypeCoverage:
    """Analyze type coverage in Python file."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return TypeCoverage(typed_functions=0, total_functions=0, type_coverage=0.0)

    total_functions = 0
    typed_functions = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_functions += 1
            if _function_has_annotations(node):
                typed_functions += 1

    coverage = (typed_functions / total_functions * 100) if total_functions > 0 else 100.0

    return TypeCoverage(
        typed_functions=typed_functions,
        total_functions=total_functions,
        type_coverage=round(coverage, 1),
    )


def _read_text_or_empty(file_path: Path) -> str:
    """Read a file's text, returning an empty string on OS errors."""
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _build_module_to_file(project_path: Path, all_files: list[Path]) -> dict[str, str]:
    """Map dotted module names (full and src.-stripped) to relative file paths."""
    module_to_file: dict[str, str] = {}
    for file_path in all_files:
        if file_path.suffix != ".py":
            continue
        rel_path = file_path.relative_to(project_path)
        module = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        module_to_file[module] = str(rel_path)
        if module.startswith("src."):
            module_to_file[module[4:]] = str(rel_path)  # Remove src. prefix
    return module_to_file


def _iter_matched_imports(content: str, module_to_file: dict[str, str]) -> Iterator[str]:
    """Yield the mapped file path for each import statement in content."""
    for line in content.split("\n"):
        if match := _IMPORT_RE.match(line.strip()):
            module = next(group for group in match.groups() if group)
            if module in module_to_file:
                yield module_to_file[module]


def _calculate_fan_in(project_path: Path, all_files: list[Path]) -> dict[str, int]:
    """Calculate fan-in: how many files import each file."""
    module_to_file = _build_module_to_file(project_path, all_files)

    fan_in: dict[str, int] = defaultdict(int)
    for file_path in all_files:
        if file_path.suffix != ".py":
            continue
        content = _read_text_or_empty(file_path)
        for imported_file in _iter_matched_imports(content, module_to_file):
            fan_in[imported_file] += 1

    return dict(fan_in)


_IGNORE_PATTERNS = ["__pycache__", ".venv", "venv", "dist", "build", ".git", "node_modules"]


def _find_source_files(project_path: Path, file_filter: set[str]) -> list[Path]:
    """Find all files matching the given extensions, excluding ignore patterns."""
    all_files: list[Path] = []
    for ext in file_filter:
        all_files.extend(project_path.rglob(f"*{ext}"))

    return [f for f in all_files if not any(pattern in str(f) for pattern in _IGNORE_PATTERNS)]


def _build_file_metrics(
    project_path: Path,
    file_path: Path,
    fan_in_map: dict[str, int],
) -> FileMetrics | None:
    """Compute metrics for a single file, or None if it cannot be read."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

    rel_path = str(file_path.relative_to(project_path))
    counts = _count_lines(content)
    imports = _analyze_imports(content, rel_path)
    types = _analyze_types(content)

    return FileMetrics(
        file_path=rel_path,
        lines_of_code=counts.lines_of_code,
        lines_of_comments=counts.lines_of_comments,
        blank_lines=counts.blank_lines,
        cyclomatic_complexity=_calculate_cyclomatic_complexity(content),
        fan_in=fan_in_map.get(rel_path, 0),
        fan_out=imports.fan_out,
        typed_functions=types.typed_functions,
        total_functions=types.total_functions,
        type_coverage=types.type_coverage,
        stdlib_imports=imports.stdlib_imports,
        third_party_imports=imports.third_party_imports,
        local_imports=imports.local_imports,
    )


def collect_file_metrics(
    project_path: Path,
    file_filter: set[str] | None = None,
) -> list[FileMetrics]:
    """Collect comprehensive metrics for all files in project.

    Args:
        project_path: Root of project
        file_filter: File extensions to include (e.g., {'.py'})

    Returns:
        List of FileMetrics sorted by cyclomatic_complexity desc
    """
    if file_filter is None:
        file_filter = {".py"}

    all_files = _find_source_files(project_path, file_filter)
    fan_in_map = _calculate_fan_in(project_path, all_files)

    metrics = [m for m in (_build_file_metrics(project_path, f, fan_in_map) for f in all_files) if m is not None]

    # Sort by cyclomatic complexity descending
    return sorted(metrics, key=lambda x: x.cyclomatic_complexity, reverse=True)


def get_high_complexity_files(
    metrics: list[FileMetrics],
    cc_threshold: int = 10,
    fan_out_threshold: int = 15,
) -> list[FileMetrics]:
    """Filter files with high complexity or coupling."""
    return [m for m in metrics if m.cyclomatic_complexity >= cc_threshold or m.fan_out >= fan_out_threshold]


def get_poorly_typed_files(
    metrics: list[FileMetrics],
    coverage_threshold: float = 50.0,
) -> list[FileMetrics]:
    """Filter files with low type coverage."""
    return [m for m in metrics if m.type_coverage < coverage_threshold and m.total_functions > 0]
