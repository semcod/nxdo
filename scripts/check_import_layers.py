#!/usr/bin/env python3
"""Import-layer lint for the nxdo package (PLF-138 seam enforcement).

Enforces the layering rules documented in docs/architecture.md:

1. Every internal import must point at the same layer or a lower layer
   (no upward imports, no cycles by construction).
2. Internal imports inside src/nxdo must use the relative form
   (`from .models import ...`), never absolute `nxdo.*` imports, so
   directory-level coupling analysis counts one cluster instead of two.

The check is AST-based (stdlib only) so it also sees lazy imports inside
function bodies. Run: python scripts/check_import_layers.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_ROOT = REPO_ROOT / "src" / "nxdo"
PACKAGE = "nxdo"

# Layer map: lower number = deeper layer. See docs/architecture.md.
LAYERS: dict[str, int] = {
    # L0 foundation: no internal imports.
    f"{PACKAGE}.autoupdate": 0,
    f"{PACKAGE}.config": 0,
    f"{PACKAGE}.koru_context": 0,
    f"{PACKAGE}.text_builder": 0,
    # L1 domain models.
    f"{PACKAGE}.models": 1,
    # L2 collectors, renderers and provider adapters.
    f"{PACKAGE}.git_reader": 2,
    f"{PACKAGE}.project_analyzer": 2,
    f"{PACKAGE}.metrics": 2,
    f"{PACKAGE}.metrics.complexity": 2,
    f"{PACKAGE}.metrics.coupling": 2,
    f"{PACKAGE}.metrics.hotspots": 2,
    f"{PACKAGE}.providers": 2,
    f"{PACKAGE}.providers.base": 2,
    f"{PACKAGE}.providers.openai_compat": 2,
    f"{PACKAGE}.llm_client": 2,
    f"{PACKAGE}.output": 2,
    f"{PACKAGE}.ticket_generator": 2,
    # L3 orchestration.
    f"{PACKAGE}.planner": 3,
    # L4 entry points and the public facade.
    f"{PACKAGE}": 4,
    f"{PACKAGE}.cli": 4,
    f"{PACKAGE}.__main__": 4,
}

VIOLATION_HINTS = {
    "layer": "move the import target to a lower layer or the importer to a higher layer (docs/architecture.md)",
    "style": "use the relative form (from .module import ...) inside src/nxdo",
    "unknown": "add the new module to the LAYERS map in scripts/check_import_layers.py",
}


def module_name(path: Path) -> str:
    rel = path.relative_to(PACKAGE_ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join([PACKAGE, *parts]) if parts else PACKAGE


def _resolve_relative_anchor(source_module: str, is_package_init: bool, level: int) -> list[str] | None:
    base_parts = source_module.split(".") if source_module != PACKAGE else [PACKAGE]
    if not is_package_init and base_parts:
        base_parts.pop()
    for _ in range(level - 1):
        if not base_parts:
            return None
        base_parts.pop()
    return base_parts


def _resolve_relative_import(node: ast.ImportFrom, source_module: str, is_package_init: bool) -> list[str]:
    base_parts = _resolve_relative_anchor(source_module, is_package_init, node.level)
    if base_parts is None:
        return []
    if node.module:
        return [".".join([*base_parts, node.module])]
    package = ".".join(base_parts)
    return [f"{package}.{alias.name}" for alias in node.names if f"{package}.{alias.name}" in LAYERS]


def resolve_import(node: ast.ImportFrom, source_module: str, is_package_init: bool) -> list[str]:
    """Resolve an ImportFrom to candidate internal module names."""
    if node.level == 0:
        base = node.module or ""
        return [base] if base == PACKAGE or base.startswith(PACKAGE + ".") else []
    return _resolve_relative_import(node, source_module, is_package_init)


def _format_violation(path: Path, node: ast.AST, kind: str, source_module: str, target: str) -> str:
    line = getattr(node, "lineno", "?")
    return f"{path.relative_to(REPO_ROOT)}:{line}: {kind} violation: {source_module} -> {target} ({VIOLATION_HINTS[kind]})"


def _check_import(node: ast.Import, path: Path, source_module: str) -> list[str]:
    violations: list[str] = []
    for alias in node.names:
        target = alias.name
        if target == PACKAGE or target.startswith(PACKAGE + "."):
            violations.append(_format_violation(path, node, "style", source_module, target))
    return violations


def _check_import_from(
    node: ast.ImportFrom, path: Path, source_module: str, source_layer: int, is_package_init: bool
) -> list[str]:
    violations: list[str] = []
    for target in resolve_import(node, source_module, is_package_init):
        if target not in LAYERS:
            violations.append(_format_violation(path, node, "unknown", source_module, target))
            continue
        if node.level == 0:
            violations.append(_format_violation(path, node, "style", source_module, target))
        if LAYERS[target] > source_layer:
            violations.append(_format_violation(path, node, "layer", source_module, target))
    return violations


def _check_node(
    node: ast.AST, path: Path, source_module: str, source_layer: int, is_package_init: bool
) -> list[str]:
    if isinstance(node, ast.Import):
        return _check_import(node, path, source_module)
    if isinstance(node, ast.ImportFrom):
        return _check_import_from(node, path, source_module, source_layer, is_package_init)
    return []


def check_file(path: Path) -> list[str]:
    source_module = module_name(path)
    source_layer = LAYERS[source_module]
    is_package_init = path.name == "__init__.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[str] = []
    for node in ast.walk(tree):
        violations.extend(_check_node(node, path, source_module, source_layer, is_package_init))
    return violations


def main() -> int:
    files = sorted(PACKAGE_ROOT.rglob("*.py"))
    violations: list[str] = []
    for path in files:
        name = module_name(path)
        if name not in LAYERS:
            violations.append(f"{path.relative_to(REPO_ROOT)}: unknown violation: module {name!r} is missing from the LAYERS map ({VIOLATION_HINTS['unknown']})")
            continue
        violations.extend(check_file(path))
    if violations:
        print(f"import-layer check failed ({len(violations)} violation(s)):", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1
    print(f"import-layer check passed: {len(files)} modules conform to the layering rules (docs/architecture.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
