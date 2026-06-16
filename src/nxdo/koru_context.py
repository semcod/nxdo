"""Koru integration schema provider for nxdo's LLM planner.

Loads the full koru integration catalog and current project state from koru
(planfile tickets, topology, doctor report) and formats it as structured
context for the LLM prompt. This allows nxdo to generate tasks that reference
specific koru operations as their implementation steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KoruOperation:
    """A single koru operation available for task planning."""
    id: str
    title: str
    description: str
    transport: str
    methods: tuple[str, ...]
    tags: tuple[str, ...]
    cli_equivalent: str | None = None


@dataclass
class KoruProjectState:
    """Current project state as seen by koru."""
    open_tickets: list[dict[str, Any]] = field(default_factory=list)
    doctor_ok: bool = True
    doctor_issues: list[str] = field(default_factory=list)
    topology_components: list[str] = field(default_factory=list)
    active_queue: list[str] = field(default_factory=list)


@dataclass
class KoruContext:
    """Full koru context for enriching the nxdo LLM prompt."""
    available: bool  # Whether koruapi is installed and reachable
    operations: list[KoruOperation]
    project_state: KoruProjectState
    schema_text: str  # Pre-formatted text for LLM prompt


# ---------------------------------------------------------------------------
# Schema loader
# ---------------------------------------------------------------------------

def _load_operations() -> list[KoruOperation]:
    """Load koru integration catalog."""
    try:
        from koruapi.integrations import list_integrations
        specs = list_integrations()
        return [
            KoruOperation(
                id=spec.id,
                title=spec.title,
                description=spec.description,
                transport=spec.transport,
                methods=spec.methods,
                tags=spec.tags,
                cli_equivalent=spec.cli_equivalent,
            )
            for spec in specs
        ]
    except ImportError:
        return []


def _load_project_state(project_path: Path) -> KoruProjectState:
    """Load current project state via koru APIs."""
    state = KoruProjectState()

    # Load open planfile tickets
    try:
        from koruapi.invoke import invoke_integration
        result = invoke_integration(
            "planfile.tickets",
            project=project_path,
            method="list",
            body={"status": "open"},
        )
        if result.get("ok"):
            state.open_tickets = result.get("tickets", [])[:10]
    except Exception:
        pass

    # Load doctor status
    try:
        from koruapi.invoke import invoke_integration
        result = invoke_integration(
            "doctor.run",
            project=project_path,
            method="run",
            body={},
        )
        if result.get("ok") is not None:
            report = result.get("report", {})
            state.doctor_ok = result.get("ok", True)
            state.doctor_issues = [
                f"{check}: {msg}"
                for check, msg in report.get("failures", {}).items()
            ]
    except Exception:
        pass

    return state


# ---------------------------------------------------------------------------
# Text formatters
# ---------------------------------------------------------------------------

# Group operations by domain for better LLM comprehension
_DOMAIN_LABELS = {
    "planfile": "📋 Ticket & Sprint Management",
    "llm": "🧠 LLM Planning",
    "ide": "💻 IDE Automation",
    "quality": "✅ Quality Gates",
    "queue": "⚙️ Queue & Automation",
    "mcp": "🔌 MCP Tools",
    "autonomous": "🤖 Autonomous Loop",
    "config": "🗂️ Configuration",
    "dsl": "📜 DSL / OQL",
    "health": "🏥 Health & Diagnostics",
    "events": "📡 Events",
    "http": "🌐 HTTP / Dashboard",
    "nxdo": "🛤️ nxdo Planning",
}


def _format_operations_for_llm(operations: list[KoruOperation]) -> str:
    """Format koru operations as structured text for LLM prompt."""
    # Group by primary tag
    by_domain: dict[str, list[KoruOperation]] = {}
    for op in operations:
        primary_tag = op.tags[0] if op.tags else "other"
        by_domain.setdefault(primary_tag, []).append(op)

    lines: list[str] = ["Available koru operations (use integration IDs in task steps):"]
    lines.append("")

    for tag, ops in sorted(by_domain.items()):
        label = _DOMAIN_LABELS.get(tag, f"[{tag}]")
        lines.append(f"  {label}")
        for op in ops:
            methods_str = " | ".join(op.methods) if op.methods else "invoke"
            lines.append(f"    [{op.id}] {op.title}")
            lines.append(f"      Methods: {methods_str}")
            lines.append(f"      {op.description}")
            if op.cli_equivalent:
                lines.append(f"      CLI: {op.cli_equivalent}")
        lines.append("")

    return "\n".join(lines)


def _format_project_state_for_llm(state: KoruProjectState) -> str:
    """Format current koru project state for LLM prompt."""
    lines: list[str] = []

    if state.open_tickets:
        lines.append(f"Open planfile tickets ({len(state.open_tickets)}):")
        for t in state.open_tickets[:5]:
            tid = t.get("id", "?")
            name = t.get("name", t.get("title", "?"))
            status = t.get("status", "open")
            priority = t.get("priority", "normal")
            lines.append(f"  [{tid}] {name} ({status}, {priority})")
        if len(state.open_tickets) > 5:
            lines.append(f"  ... and {len(state.open_tickets) - 5} more")
    else:
        lines.append("Open planfile tickets: none")

    if not state.doctor_ok:
        lines.append("")
        lines.append("Project health issues (koru doctor):")
        for issue in state.doctor_issues[:5]:
            lines.append(f"  ⚠ {issue}")

    return "\n".join(lines) if lines else "Project state: clean, no open issues."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_koru_context(
    project_path: Path,
    include_project_state: bool = True,
) -> KoruContext:
    """Build full koru context for nxdo's LLM prompt.

    Args:
        project_path: Path to project root
        include_project_state: Whether to query live project state (tickets, doctor)
                                Set to False for faster dry-run mode.

    Returns:
        KoruContext with operations, state, and pre-formatted schema_text.
    """
    operations = _load_operations()
    if not operations:
        return KoruContext(
            available=False,
            operations=[],
            project_state=KoruProjectState(),
            schema_text="",
        )

    state = _load_project_state(project_path) if include_project_state else KoruProjectState()

    ops_text = _format_operations_for_llm(operations)
    state_text = _format_project_state_for_llm(state)

    schema_text = "\n".join([
        "=== KORU INTEGRATION SCHEMA ===",
        "",
        ops_text,
        "=== CURRENT PROJECT STATE (koru) ===",
        "",
        state_text,
    ])

    return KoruContext(
        available=True,
        operations=operations,
        project_state=state,
        schema_text=schema_text,
    )


def get_koru_system_prompt_extension() -> str:
    """Return system prompt extension for koru-aware planning mode.

    When koru schema is available, instruct the LLM to:
    - Reference specific koru operations in task implementation steps
    - Prioritize tasks based on open planfile tickets
    - Generate tasks that form a complete koru workflow
    """
    return """\

KORU-AWARE PLANNING MODE:
You have access to the koru integration catalog. When generating tasks:

DESCRIPTION RULES (CRITICAL):
- Each task MUST have a detailed 2-4 sentence description explaining WHAT to do and WHY
- Include specific file paths, function names, or components to modify
- Mention the expected outcome or benefit of completing the task
- NEVER leave description empty or use only generic text

ACCEPTANCE CRITERIA RULES:
- Provide 2-4 concrete, verifiable acceptance criteria per task
- Criteria should be testable (e.g., "Tests pass", "Function X has CC < 10")
- Include criteria about koru integration if applicable

1. REFERENCE KORU OPERATIONS: In each task's description, specify which koru
   operation(s) implement it. Use the format:
   "Implementation: invoke koru [integration_id] with method [method]"
   Example: "Implementation: invoke koru autopilot.drive to inject refactoring prompt"

2. WORKFLOW SEQUENCING: Generate tasks that form a logical koru pipeline:
   - Analysis tasks should use: doctor.run, scan.apply, nxdo.plan (dry_run)
   - Implementation tasks: autopilot.drive, queue.loop (once)
   - Verification tasks: mcp.quality_gates, gate.regix
   - Sync tasks: planfile.tickets (list), nxdo.plan (sync_planfile)

3. PLANFILE INTEGRATION: If open tickets exist, the first task should
   RESOLVE them by processing through koru queue, not just list them.

4. AVOID DUPLICATION: Do not generate tasks for work already tracked in
   open planfile tickets.

5. TASK TYPES for koru workflows:
   - "chore": koru infrastructure tasks (doctor, scan, sync)
   - "refactor": autopilot-driven code changes
   - "test": quality gate runs, test coverage improvements
   - "feature": new capabilities implemented via autopilot.drive

Add "koru_operation" field to each task with the primary integration ID.
"""
