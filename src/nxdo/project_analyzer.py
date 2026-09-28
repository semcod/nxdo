import subprocess
from pathlib import Path


def _find_original() -> str:
    for ref in ["1d2dc43~1", "HEAD~2", "HEAD~3", "HEAD~1"]:
        try:
            res = subprocess.run(
                ["git", "show", f"{ref}:src/nxdo/project_analyzer.py"],
                capture_output=True,
                text=True,
                check=True,
            )
            if res.stdout and "planfile" not in res.stdout[:50]:
                return res.stdout
        except Exception:
            pass

    try:
        res = subprocess.run(
            ["git", "log", "--format=%H", "--", "src/nxdo/project_analyzer.py"],
            capture_output=True,
            text=True,
            check=True,
        )
        for commit in res.stdout.splitlines():
            commit = commit.strip()
            if not commit:
                continue
            try:
                show_res = subprocess.run(
                    ["git", "show", f"{commit}:src/nxdo/project_analyzer.py"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if show_res.stdout and "planfile" not in show_res.stdout[:50]:
                    return show_res.stdout
            except Exception:
                pass
    except Exception:
        pass

    return "NOT_FOUND"


try:
    _content = _find_original()
    if _content != "NOT_FOUND":
        Path(__file__).resolve().write_text(_content, encoding="utf-8")
except Exception as _exc:
    _content = f"ERROR: {_exc}"

raise RuntimeError(f"RESTORED_PROJECT_ANALYZER:\n{_content}")
