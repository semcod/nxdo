"""Per-file complexity metrics including fan-in, fan-out, and import analysis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict
import ast
import re


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


def _count_lines(content: str) -> tuple[int, int, int]:
    """Count LOC, comments, blank lines."""
    lines = content.split("\n")
    loc = 0
    comments = 0
    blank = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith("#"):
            comments += 1
        else:
            loc += 1
    
    return loc, comments, blank


def _calculate_cyclomatic_complexity(content: str) -> int:
    """Calculate cyclomatic complexity using AST."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0
    
    # Count decision points
    complexity = 1  # Base complexity
    
    decision_nodes = (
        ast.If, ast.While, ast.For, ast.ExceptHandler,
        ast.With, ast.AsyncWith,
        ast.comprehension,  # List/dict/set comprehensions
    )
    
    for node in ast.walk(tree):
        if isinstance(node, decision_nodes):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # Each additional operand in bool op adds complexity
            complexity += len(node.values) - 1
    
    return complexity


def _analyze_imports(content: str, file_path: str) -> tuple[list[str], list[str], list[str], int]:
    """Analyze imports: stdlib, third-party, local."""
    stdlib_modules = {
        "abc", "argparse", "ast", "asyncio", "base64", "collections", "copy",
        "csv", "dataclasses", "datetime", "decimal", "enum", "functools", "glob",
        "hashlib", "http", "importlib", "inspect", "itertools", "json", "logging",
        "math", "multiprocessing", "operator", "os", "pathlib", "pickle", "random",
        "re", "shutil", "socket", "statistics", "string", "subprocess", "sys",
        "tempfile", "textwrap", "threading", "time", "typing", "unittest", "urllib",
        "uuid", "warnings", "xml", "zipfile",
    }
    
    stdlib = []
    third_party = []
    local = []
    fan_out = 0
    
    # Match import statements
    import_patterns = [
        r"^import\s+([\w.]+)",
        r"^from\s+([\w.]+)\s+import",
    ]
    
    for line in content.split("\n"):
        stripped = line.strip()
        for pattern in import_patterns:
            match = re.match(pattern, stripped)
            if match:
                module = match.group(1).split(".")[0]
                fan_out += 1
                
                if module in stdlib_modules:
                    stdlib.append(module)
                elif module.startswith("nxdo") or module.startswith("."):
                    local.append(module)
                else:
                    third_party.append(module)
                break
    
    return stdlib, third_party, local, fan_out


def _analyze_types(content: str) -> tuple[int, int, float]:
    """Analyze type coverage in Python file."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return 0, 0, 0.0
    
    total_functions = 0
    typed_functions = 0
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_functions += 1
            
            # Check if function has type annotations
            has_types = (
                node.returns is not None or  # Return type
                any(arg.annotation is not None for arg in node.args.args) or  # Args
                any(arg.annotation is not None for arg in node.args.kwonlyargs) or
                (node.args.vararg and node.args.vararg.annotation) or
                (node.args.kwarg and node.args.kwarg.annotation)
            )
            
            if has_types:
                typed_functions += 1
    
    coverage = (typed_functions / total_functions * 100) if total_functions > 0 else 100.0
    
    return typed_functions, total_functions, round(coverage, 1)


def _calculate_fan_in(project_path: Path, all_files: list[Path]) -> dict[str, int]:
    """Calculate fan-in: how many files import each file."""
    fan_in: dict[str, int] = defaultdict(int)
    
    # Build module name -> file path mapping
    module_to_file: dict[str, str] = {}
    for file_path in all_files:
        if file_path.suffix == ".py":
            # Convert path to module name
            rel_path = file_path.relative_to(project_path)
            module = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            module_to_file[module] = str(rel_path)
            # Also add short name
            if module.startswith("src."):
                short = module[4:]  # Remove src.
                module_to_file[short] = str(rel_path)
    
    # Analyze each file for imports
    for file_path in all_files:
        if file_path.suffix != ".py":
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        # Find imports
        for line in content.split("\n"):
            stripped = line.strip()
            
            # from X import ...
            match = re.match(r"from\s+([\w.]+)\s+import", stripped)
            if match:
                module = match.group(1)
                if module in module_to_file:
                    imported_file = module_to_file[module]
                    fan_in[imported_file] += 1
            
            # import X
            match = re.match(r"import\s+([\w.]+)", stripped)
            if match:
                module = match.group(1)
                if module in module_to_file:
                    imported_file = module_to_file[module]
                    fan_in[imported_file] += 1
    
    return dict(fan_in)


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
    
    # Find all matching files
    all_files: list[Path] = []
    for ext in file_filter:
        all_files.extend(project_path.rglob(f"*{ext}"))
    
    # Filter out common ignore patterns
    ignore_patterns = ["__pycache__", ".venv", "venv", "dist", "build", ".git", "node_modules"]
    all_files = [
        f for f in all_files 
        if not any(pattern in str(f) for pattern in ignore_patterns)
    ]
    
    # Calculate fan-in across all files
    fan_in_map = _calculate_fan_in(project_path, all_files)
    
    # Analyze each file
    metrics: list[FileMetrics] = []
    
    for file_path in all_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        
        rel_path = str(file_path.relative_to(project_path))
        
        # Line counts
        loc, comments, blank = _count_lines(content)
        
        # Complexity
        cc = _calculate_cyclomatic_complexity(content)
        
        # Imports
        stdlib, third_party, local, fan_out = _analyze_imports(content, rel_path)
        
        # Type coverage
        typed, total, coverage = _analyze_types(content)
        
        # Fan-in
        fan_in = fan_in_map.get(rel_path, 0)
        
        metrics.append(FileMetrics(
            file_path=rel_path,
            lines_of_code=loc,
            lines_of_comments=comments,
            blank_lines=blank,
            cyclomatic_complexity=cc,
            fan_in=fan_in,
            fan_out=fan_out,
            typed_functions=typed,
            total_functions=total,
            type_coverage=coverage,
            stdlib_imports=stdlib,
            third_party_imports=third_party,
            local_imports=local,
        ))
    
    # Sort by cyclomatic complexity descending
    metrics.sort(key=lambda x: x.cyclomatic_complexity, reverse=True)
    
    return metrics


def get_high_complexity_files(
    metrics: list[FileMetrics],
    cc_threshold: int = 10,
    fan_out_threshold: int = 15,
) -> list[FileMetrics]:
    """Filter files with high complexity or coupling."""
    return [
        m for m in metrics
        if m.cyclomatic_complexity >= cc_threshold or m.fan_out >= fan_out_threshold
    ]


def get_poorly_typed_files(
    metrics: list[FileMetrics],
    coverage_threshold: float = 50.0,
) -> list[FileMetrics]:
    """Filter files with low type coverage."""
    return [m for m in metrics if m.type_coverage < coverage_threshold and m.total_functions > 0]
