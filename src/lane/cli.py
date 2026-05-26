"""CLI for generating the next 10 project tasks."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .config import get_settings
from .git_reader import read_git_context
from .llm_client import build_user_prompt
from .output import render_context, render_plan, render_plan_json
from .planner import generate_next_tasks
from .project_analyzer import analyze_project
from .providers import OpenAICompatProvider
from .ticket_generator import export_to_planfile_yaml, sync_to_planfile, sync_to_todo_md, task_plan_to_tickets

app = typer.Typer(
    name="lane",
    help="Generate a 10-task engineering plan from project state, git history and LLM context.",
    no_args_is_help=False,
    add_completion=False,
)

console = Console()
err_console = Console(stderr=True)


@app.command("plan")
def cmd_plan(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    extra_context: str = typer.Option("", "--extra-context", "-e", help="Additional prompt context."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the LLM model name."),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="Override the API base URL."),
    as_json: bool = typer.Option(False, "--json", help="Output plan as JSON."),
    max_commits: int = typer.Option(30, "--max-commits", help="How many recent commits to inspect."),
) -> None:
    """Generate a 10-task plan for the repository."""
    cfg = get_settings()
    if max_commits != 30:
        cfg.max_commits = max_commits  # type: ignore[misc]

    provider = OpenAICompatProvider(model=model, base_url=base_url, settings=cfg)

    try:
        plan = generate_next_tasks(
            repo_path=repo.resolve(),
            extra_context=extra_context,
            provider=provider,
            settings=cfg,
        )
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    if as_json:
        render_plan_json(plan, console)
    else:
        render_plan(plan, console)


@app.command("print-context")
def cmd_print_context(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    max_commits: int = typer.Option(30, "--max-commits", help="How many recent commits to inspect."),
    raw: bool = typer.Option(False, "--raw", help="Print raw text instead of Rich panels."),
) -> None:
    """Print the assembled project and git context (no LLM call)."""
    snapshot = analyze_project(repo.resolve())
    git_ctx = read_git_context(repo.resolve(), max_commits=max_commits)
    project_text = snapshot.to_text()
    git_text = git_ctx.to_text()

    if raw:
        print(project_text)
        print(git_text)
    else:
        render_context(project_text, git_text, console)


@app.command("print-prompt")
def cmd_print_prompt(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    extra_context: str = typer.Option("", "--extra-context", "-e", help="Additional prompt context."),
    max_commits: int = typer.Option(30, "--max-commits", help="How many recent commits to inspect."),
) -> None:
    """Print the full prompt that would be sent to the LLM."""
    snapshot = analyze_project(repo.resolve())
    git_ctx = read_git_context(repo.resolve(), max_commits=max_commits)
    prompt = build_user_prompt(snapshot.to_text(), git_ctx.to_text(), extra_context)
    print(prompt)


@app.command("validate")
def cmd_validate(
    plan_file: Path = typer.Argument(..., help="Path to a JSON plan file to validate."),
) -> None:
    """Validate a saved JSON plan file against the TaskPlan schema."""
    from .models import TaskPlan

    try:
        data = json.loads(plan_file.read_text(encoding="utf-8"))
        plan = TaskPlan.model_validate(data)
    except (json.JSONDecodeError, ValueError) as exc:
        err_console.print(f"[bold red]Validation failed:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✓[/bold green] Plan '{plan.project_name}' is valid ({len(plan.tasks)} tasks).")


@app.command("tickets")
def cmd_tickets(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    extra_context: str = typer.Option("", "--extra-context", "-e", help="Additional prompt context."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the LLM model name."),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="Override the API base URL."),
    max_commits: int = typer.Option(30, "--max-commits", help="How many recent commits to inspect."),
    sync_todo: bool = typer.Option(False, "--sync-todo", help="Append tasks to TODO.md as checkboxes."),
    sync_planfile: bool = typer.Option(False, "--sync-planfile", help="Store tickets in .planfile/ and sync with markdown."),
    export_yaml: bool = typer.Option(False, "--export-yaml", help="Export to planfile YAML format."),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for YAML export."),
) -> None:
    """Generate tickets from a plan using planfile integration."""
    cfg = get_settings()
    if max_commits != 30:
        cfg.max_commits = max_commits  # type: ignore[misc]

    provider = OpenAICompatProvider(model=model, base_url=base_url, settings=cfg)

    try:
        plan = generate_next_tasks(
            repo_path=repo.resolve(),
            extra_context=extra_context,
            provider=provider,
            settings=cfg,
        )
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    # Generate tickets from plan
    tickets = task_plan_to_tickets(plan)
    console.print(f"[green]✓[/green] Generated {len(tickets)} tickets from plan")

    # Sync to TODO.md if requested
    if sync_todo:
        report = sync_to_todo_md(plan, repo.resolve())
        todo_path = report.get("todo_path", "TODO.md")
        console.print(f"[green]✓[/green] Appended {report.get('updated', 0)} tasks to {todo_path}")

    # Sync to .planfile/ store and markdown if requested
    if sync_planfile:
        report = sync_to_planfile(plan, repo.resolve())
        if not report.get("enabled"):
            console.print("[yellow]⚠[/yellow] planfile not available")

    # Export to planfile YAML if requested
    if export_yaml:
        output = output_path or repo.resolve() / "strategy.yaml"
        export_to_planfile_yaml(plan, output)

    # Display tickets
    for ticket in tickets:
        priority = ticket.get("priority", "medium")
        priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
        console.print(f"{priority_emoji} [{ticket['id']}] {ticket['title']}")
        if ticket.get("description"):
            console.print(f"    {ticket['description'][:100]}...")


def app_entry() -> None:
    """Entry point used by the installed `lane` script."""
    app()


# ---------------------------------------------------------------------------
# Legacy compatibility: keep `main()` so existing callers (tests, __main__)
# continue to work using argparse-style argv lists.
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """Compatibility shim — maps legacy argparse argv to Typer sub-commands."""
    import argparse

    parser = argparse.ArgumentParser(prog="lane", add_help=False)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--extra-context", default="")
    parser.add_argument("--max-commits", type=int, default=30)
    parser.add_argument("--model", default=None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--print-prompt", action="store_true")
    parser.add_argument("--json", action="store_true")
    args, _ = parser.parse_known_args(argv)

    repo_path = Path(args.repo).resolve()
    if args.print_prompt:
        snapshot = analyze_project(repo_path)
        git_ctx = read_git_context(repo_path, max_commits=args.max_commits)
        prompt = build_user_prompt(snapshot.to_text(), git_ctx.to_text(), args.extra_context)
        print(prompt)
        return 0

    cfg = get_settings()
    provider = OpenAICompatProvider(model=args.model, base_url=args.base_url, settings=cfg)
    try:
        plan = generate_next_tasks(
            repo_path=repo_path,
            extra_context=args.extra_context,
            provider=provider,
            settings=cfg,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2))
    else:
        print(plan)
    return 0
