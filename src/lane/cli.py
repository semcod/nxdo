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
from .models import TaskPlan
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


def _sync_todos_if_requested(plan: TaskPlan, repo: Path, sync_todo: bool) -> None:
    """Sync tasks to TODO.md if requested."""
    if not sync_todo:
        return
    report = sync_to_todo_md(plan, repo)
    todo_path = report.get("todo_path", "TODO.md")
    console.print(f"[green]✓[/green] Synced {report.get('updated', 0)} tasks to {todo_path}")


def _sync_planfile_if_requested(plan: TaskPlan, repo: Path, sync_planfile: bool) -> None:
    """Sync tickets to .planfile/ if requested."""
    if not sync_planfile:
        return
    report = sync_to_planfile(plan, repo)
    if not report.get("enabled"):
        console.print("[yellow]⚠[/yellow] planfile not available")


def _export_yaml_if_requested(plan: TaskPlan, repo: Path, export_yaml: bool, output_path: Optional[Path]) -> None:
    """Export to planfile YAML if requested."""
    if not export_yaml:
        return
    output = output_path or repo / "strategy.yaml"
    export_to_planfile_yaml(plan, output)


def _get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level."""
    return {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")


def _display_tickets(tickets: list[dict[str, str]]) -> None:
    """Display tickets with priority emojis."""
    for ticket in tickets:
        priority = ticket.get("priority", "medium")
        priority_emoji = _get_priority_emoji(priority)
        console.print(f"{priority_emoji} [{ticket['id']}] {ticket['title']}")
        if ticket.get("description"):
            console.print(f"    {ticket['description'][:100]}...")


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
    koru_aware: bool = typer.Option(False, "--koru-aware", help="Enable koru integration schema for smart task planning."),
) -> None:
    """Generate tickets from a plan using planfile integration."""
    cfg = get_settings()
    if max_commits != 30:
        cfg.max_commits = max_commits  # type: ignore[misc]

    provider = OpenAICompatProvider(
        model=model, base_url=base_url, settings=cfg, koru_aware=koru_aware
    )

    try:
        plan = generate_next_tasks(
            repo_path=repo.resolve(),
            extra_context=extra_context,
            provider=provider,
            settings=cfg,
            koru_aware=koru_aware,
        )
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    tickets = task_plan_to_tickets(plan)
    console.print(f"[green]✓[/green] Generated {len(tickets)} tickets from plan")

    _sync_todos_if_requested(plan, repo.resolve(), sync_todo)
    _sync_planfile_if_requested(plan, repo.resolve(), sync_planfile)
    _export_yaml_if_requested(plan, repo.resolve(), export_yaml, output_path)
    _display_tickets(tickets)


@app.command("metrics")
def cmd_metrics(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    top: int = typer.Option(10, "--top", "-n", help="Show top N items per category."),
    min_coupling: float = typer.Option(0.3, "--min-coupling", help="Minimum coupling score to display."),
) -> None:
    """Display code metrics: complexity, coupling, hotspots."""
    from lane.metrics import (
        collect_coupling_matrix,
        get_coupling_clusters,
        identify_bug_hotspots,
        calculate_bus_factor,
        collect_file_metrics,
    )

    repo_path = repo.resolve()
    console.print(f"[bold]Code Metrics for {repo_path.name}[/bold]\n")

    # 1. Complexity Metrics
    console.print("[bold cyan]Top Files by Cyclomatic Complexity[/bold cyan]")
    file_metrics = collect_file_metrics(repo_path, file_filter={".py"})
    for m in file_metrics[:top]:
        if m.cyclomatic_complexity > 5:
            console.print(f"  CC={m.cyclomatic_complexity:3d} | {m.file_path}")
    console.print()

    # 2. Coupling Analysis
    console.print(f"[bold cyan]Top Coupled File Pairs (>{min_coupling})[/bold cyan]")
    coupling = collect_coupling_matrix(repo_path, min_coupling=min_coupling, file_filter={".py"})
    for c in coupling[:top]:
        console.print(f"  {c.coupling_score:.2f} | {c.file_a} <-> {c.file_b}")
    console.print()

    # 3. Coupling Clusters (sprint groupings)
    clusters = get_coupling_clusters(coupling, min_coupling=0.5)
    if clusters:
        console.print("[bold cyan]Coupling Clusters (refactor together)[/bold cyan]")
        for i, cluster in enumerate(clusters[:5], 1):
            console.print(f"  Cluster {i} ({len(cluster)} files):")
            for f in sorted(cluster)[:5]:
                console.print(f"    - {f}")
        console.print()

    # 4. Bug Hotspots
    console.print("[bold cyan]Bug Hotspots (high churn + fixes)[/bold cyan]")
    hotspots = identify_bug_hotspots(repo_path, top_n=top)
    for h in hotspots:
        risk = "🔥" if h.bug_density > 0.3 else "⚠️"
        console.print(f"  {risk} {h.file_path}")
        console.print(f"     Bugs: {h.bug_fix_commits}/{h.total_commits} commits, Churn: {h.code_churn_lines} lines")
    console.print()

    # 5. Bus Factor
    console.print("[bold cyan]Low Bus Factor (knowledge silos)[/bold cyan]")
    bus_factors = calculate_bus_factor(repo_path, critical_threshold=2)
    for file_path, count in sorted(bus_factors.items(), key=lambda x: x[1])[:top]:
        icon = "🚨" if count == 1 else "⚠️"
        console.print(f"  {icon} {count} author(s): {file_path}")


@app.command("auto")
def cmd_auto(
    repo: Path = typer.Argument(Path("."), help="Path to the repository to analyze."),
    extra_context: str = typer.Option("", "--extra-context", "-e", help="Additional prompt context."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without executing."),
) -> None:
    """Auto-generate and sync tickets for the most important work.

    This command automatically:
    1. Analyzes the project for high-priority issues (hotspots, complexity, coupling)
    2. Generates tickets using koru-aware planning
    3. Syncs to .planfile/ for execution via koru queue

    Equivalent to: lane tickets . --koru-aware --sync-planfile
    """
    from lane.metrics import collect_file_metrics, identify_bug_hotspots

    repo_path = repo.resolve()
    console.print(f"[bold]🚀 Lane Auto Mode for {repo_path.name}[/bold]\n")

    # Quick analysis to inform user
    console.print("[dim]Analyzing project...[/dim]")

    # Check for critical issues
    hotspots = identify_bug_hotspots(repo_path, top_n=3)
    complexity = collect_file_metrics(repo_path, file_filter={".py"})
    high_cc = [m for m in complexity[:5] if m.cyclomatic_complexity > 10]

    issues_found = []
    if hotspots:
        issues_found.append(f"{len(hotspots)} bug hotspots")
    if high_cc:
        issues_found.append(f"{len(high_cc)} high-complexity files")

    if issues_found:
        console.print(f"[yellow]⚠ Found: {', '.join(issues_found)}[/yellow]")
    else:
        console.print("[green]✓ Project looks healthy[/green]")

    if dry_run:
        console.print("\n[dim]Dry run mode - would execute:[/dim]")
        console.print(f"  lane tickets {repo_path} --koru-aware --sync-planfile")
        return

    # Execute auto workflow
    console.print("\n[bold]Generating koru-aware tickets...[/bold]")

    cfg = get_settings()
    provider = OpenAICompatProvider(settings=cfg, koru_aware=True)

    try:
        plan = generate_next_tasks(
            repo_path=repo_path,
            extra_context=extra_context or "Focus on critical hotspots and technical debt",
            provider=provider,
            settings=cfg,
            koru_aware=True,
        )
    except ValueError as exc:
        err_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    tickets = task_plan_to_tickets(plan)
    console.print(f"[green]✓[/green] Generated {len(tickets)} tickets")

    # Auto-sync to planfile
    console.print("[dim]Syncing to .planfile/...[/dim]")
    _sync_planfile_if_requested(plan, repo_path, sync_planfile=True)

    # Summary
    console.print(f"\n[bold green]🎉 Done![/bold green] {len(tickets)} tickets queued in .planfile/")
    console.print("[dim]Run 'koru --queue --loop' or 'planfile apply' to execute[/dim]")


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
