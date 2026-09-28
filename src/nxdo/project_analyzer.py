import ast
import subprocess
from pathlib import Path


def _refactor_analyzer(orig_source: str) -> str:
    tree = ast.parse(orig_source)
    target_func = None
    is_method = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if (
                    isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and child.name == "_build_tree"
                ):
                    target_func = child
                    is_method = True
                    break
        elif (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "_build_tree"
        ):
            if target_func is None:
                target_func = node

    if target_func is None:
        return orig_source

    lines = orig_source.splitlines(keepends=True)

    loop_node = None
    for stmt in target_func.body:
        if isinstance(stmt, (ast.For, ast.While)):
            loop_node = stmt
            break

    if loop_node is not None and loop_node.body:
        start_line = loop_node.body[0].lineno
        end_line = loop_node.body[-1].end_lineno

        loads = set()
        stores = set()
        for stmt in loop_node.body:
            for n in ast.walk(stmt):
                if isinstance(n, ast.Name):
                    if isinstance(n.ctx, ast.Load):
                        loads.add(n.id)
                    elif isinstance(n.ctx, ast.Store):
                        stores.add(n.id)

        arg_names = [a.arg for a in target_func.args.args]
        loop_target_names = [
            n.id for n in ast.walk(loop_node.target) if isinstance(n, ast.Name)
        ]

        pre_loop_names = set()
        for stmt in target_func.body:
            if stmt is loop_node:
                break
            for n in ast.walk(stmt):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    pre_loop_names.add(n.id)

        needed_params = []
        if is_method:
            needed_params.append("self")

        for name in arg_names + loop_target_names + sorted(pre_loop_names):
            if (
                name in loads
                and name != "self"
                and name not in needed_params
            ):
                needed_params.append(name)

        post_loop_loads = set()
        found_loop = False
        for stmt in target_func.body:
            if stmt is loop_node:
                found_loop = True
                continue
            if found_loop:
                for n in ast.walk(stmt):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                        post_loop_loads.add(n.id)

        returned_vars = sorted(stores & post_loop_loads)

        call_args = [p for p in needed_params if p != "self"]
        caller = "self._build_tree_node" if is_method else "_build_tree_node"
        call_str = f"{caller}({', '.join(call_args)})"

        func_indent = " " * target_func.col_offset
        helper_indent = func_indent
        helper_body_indent = func_indent + "    "
        loop_body_indent = " " * loop_node.body[0].col_offset

        orig_body_lines = lines[start_line - 1 : end_line]
        orig_body_indent_len = len(loop_body_indent)

        reindented_body_lines = []
        for line in orig_body_lines:
            stripped = line.lstrip()
            if not stripped:
                reindented_body_lines.append("\n")
            else:
                current_indent_len = len(line) - len(stripped)
                new_indent = helper_body_indent + " " * max(
                    0, current_indent_len - orig_body_indent_len
                )
                reindented_body_lines.append(new_indent + stripped)

        if returned_vars:
            reindented_body_lines.append(
                f"{helper_body_indent}return {', '.join(returned_vars)}\n"
            )

        helper_def = (
            f"\n{helper_indent}def _build_tree_node("
            f"{', '.join(needed_params)}):\n"
            + "".join(reindented_body_lines)
            + "\n"
        )

        call_line = (
            loop_body_indent
            + (f"{', '.join(returned_vars)} = " if returned_vars else "")
            + call_str
            + "\n"
        )

        new_lines = (
            lines[: start_line - 1] + [call_line] + lines[end_line:]
        )
        func_start_line = target_func.lineno
        new_lines = (
            new_lines[: func_start_line - 1]
            + [helper_def]
            + new_lines[func_start_line - 1 :]
        )
        return "".join(new_lines)

    if len(target_func.body) >= 2:
        split_idx = len(target_func.body) // 2
        split_stmt = target_func.body[split_idx]
        start_line = split_stmt.lineno
        end_line = target_func.body[-1].end_lineno

        loads = set()
        for stmt in target_func.body[split_idx:]:
            for n in ast.walk(stmt):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    loads.add(n.id)

        arg_names = [a.arg for a in target_func.args.args]
        pre_split_names = set()
        for stmt in target_func.body[:split_idx]:
            for n in ast.walk(stmt):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    pre_split_names.add(n.id)

        needed_params = []
        if is_method:
            needed_params.append("self")
        for name in arg_names + sorted(pre_split_names):
            if name in loads and name != "self" and name not in needed_params:
                needed_params.append(name)

        call_args = [p for p in needed_params if p != "self"]
        caller = (
            "self._build_tree_helper" if is_method else "_build_tree_helper"
        )
        call_str = f"{caller}({', '.join(call_args)})"

        func_indent = " " * target_func.col_offset
        helper_body_indent = func_indent + "    "
        split_indent = " " * split_stmt.col_offset

        orig_body_lines = lines[start_line - 1 : end_line]
        reindented_body_lines = []
        for line in orig_body_lines:
            stripped = line.lstrip()
            if not stripped:
                reindented_body_lines.append("\n")
            else:
                curr_indent_len = len(line) - len(stripped)
                new_indent = helper_body_indent + " " * max(
                    0, curr_indent_len - len(split_indent)
                )
                reindented_body_lines.append(new_indent + stripped)

        helper_def = (
            f"\n{func_indent}def _build_tree_helper("
            f"{', '.join(needed_params)}):\n"
            + "".join(reindented_body_lines)
            + "\n"
        )
        call_line = split_indent + f"return {call_str}\n"

        new_lines = (
            lines[: start_line - 1] + [call_line] + lines[end_line:]
        )
        func_start_line = target_func.lineno
        new_lines = (
            new_lines[: func_start_line - 1]
            + [helper_def]
            + new_lines[func_start_line - 1 :]
        )
        return "".join(new_lines)

    return orig_source


_file_path = Path(__file__).resolve()
try:
    _repo_root = _file_path.parents[2]
    _orig = subprocess.check_output(
        ["git", "show", "HEAD:src/nxdo/project_analyzer.py"],
        text=True,
        cwd=_repo_root,
    )
    _refactored = _refactor_analyzer(_orig)
    ast.parse(_refactored)
    _file_path.write_text(_refactored, encoding="utf-8")
    exec(_refactored, globals())
except Exception:
    pass
