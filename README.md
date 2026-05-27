# lane


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.17-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.34-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-6.8h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.3367 (20 commits)
- 👤 **Human dev:** ~$678 (6.8h @ $100/h, 30min dedup)

Generated on 2026-05-27 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

`lane` is a Python package that inspects the current project state, reads recent git history, adds a user question for an LLM, and returns a concrete plan for the next 10 engineering tasks.

## What is included

- **Project snapshot analysis** — README, manifests (pyproject.toml, package.json, Cargo.toml, …), directory tree, stack detection
- **Git context** — recent commits, most-changed files, TODO/FIXME markers
- **Advanced code metrics** — cyclomatic complexity, coupling analysis, bug hotspots, bus factor detection
- **Koru-aware planning** — Deep integration with koru framework for intelligent task generation
- **Pydantic models** — validated data models for tasks and plans (`Task`, `TaskPlan`)
- **Provider abstraction** — pluggable LLM backends; ships with an OpenAI-compatible provider (works with OpenRouter and any OpenAI-style API)
- **Planner orchestrator** — `generate_next_tasks()` composes analysis + prompt + LLM call into a validated TaskPlan
- **Rich CLI** — `lane plan`, `lane auto`, `lane metrics`, `lane print-context`, `lane print-prompt`, `lane validate`, `lane tickets`
- **Reliability** — `httpx` for HTTP, `tenacity` for automatic retry/backoff, `pydantic-settings` for environment config

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
lane print-prompt .
```

To generate a real plan, set `OPENROUTER_API_KEY` or `OPENAI_API_KEY` and run:

```bash
lane plan . --extra-context "What should we build next for this repository?"
```

Output as JSON:

```bash
lane plan . --json
```

Inspect captured project and git context without calling the LLM:

```bash
lane print-context .
```

Validate a saved plan file:

```bash
lane validate plan.json
```

Analyze code metrics and coupling:

```bash
lane metrics .
```

## CLI Reference

### `lane plan`
Generate a 10-task engineering plan for a repository.

**Usage:**
```bash
lane plan [REPO_PATH] [OPTIONS]
```

**Options:**
- `--extra-context, -e TEXT`: Additional prompt context for the LLM
- `--model, -m TEXT`: Override the LLM model name
- `--base-url TEXT`: Override the API base URL
- `--json`: Output plan as JSON instead of formatted text
- `--max-commits INTEGER`: How many recent commits to inspect (default: 30)

### `lane print-context`
Print the assembled project and git context without calling the LLM.

**Usage:**
```bash
lane print-context [REPO_PATH] [OPTIONS]
```

**Options:**
- `--max-commits INTEGER`: How many recent commits to inspect (default: 30)
- `--raw`: Print raw text instead of Rich panels

### `lane print-prompt`
Print the full prompt that would be sent to the LLM.

**Usage:**
```bash
lane print-prompt [REPO_PATH] [OPTIONS]
```

**Options:**
- `--extra-context, -e TEXT`: Additional prompt context for the LLM
- `--max-commits INTEGER`: How many recent commits to inspect (default: 30)

### `lane validate`
Validate a saved JSON plan file against the TaskPlan schema.

**Usage:**
```bash
lane validate PLAN_FILE
```

### `lane auto`
Auto-generate and sync tickets for the most important work. This is the quickest way to get actionable tickets into your planfile.

**Usage:**
```bash
lane auto [REPO_PATH] [OPTIONS]
```

**What it does:**
1. Analyzes project for high-priority issues (hotspots, complexity, coupling)
2. Generates tickets using koru-aware planning
3. Auto-syncs to `.planfile/` for execution via koru queue

**Options:**
- `--extra-context, -e TEXT`: Additional prompt context for the LLM
- `--dry-run`: Show what would be done without executing

**Example:**
```bash
# Quick auto mode - analyze, generate, sync
lane auto

# With extra context
lane auto . -e "Focus on security improvements"

# Dry run to preview
lane auto --dry-run
```

**Equivalent to:**
```bash
lane tickets . --koru-aware --sync-planfile
```

### `lane metrics`
Display comprehensive code metrics for the project including cyclomatic complexity, change coupling, bug hotspots, and bus factor analysis.

**Usage:**
```bash
lane metrics [REPO_PATH] [OPTIONS]
```

**Options:**
- `--top, -n INTEGER`: Show top N items per category (default: 10)
- `--min-coupling FLOAT`: Minimum coupling score to display (default: 0.3)

**Metrics displayed:**
- **Cyclomatic Complexity** per file (identify complex functions to refactor)
- **Coupling Analysis** — which files change together frequently (plan refactors together)
- **Coupling Clusters** — groups of tightly coupled files (sprint planning)
- **Bug Hotspots** — files with high bug fix rate and code churn
- **Bus Factor** — files with few authors (knowledge silos)

**Example:**
```bash
# Show metrics for current project
lane metrics .

# Show top 5 with higher coupling threshold
lane metrics . --top 5 --min-coupling 0.5
```

### `lane tickets`
Generate tickets from a plan using planfile integration.

This command generates tickets from a TaskPlan and optionally syncs them to TODO.md, .planfile/, or exports to planfile YAML format.

**Usage:**
```bash
lane tickets [REPO_PATH] [OPTIONS]
```

**Options:**
- `--extra-context, -e TEXT`: Additional prompt context for the LLM
- `--model, -m TEXT`: Override the LLM model name
- `--base-url TEXT`: Override the API base URL
- `--max-commits INTEGER`: How many recent commits to inspect (default: 30)
- `--sync-todo`: Sync tasks to TODO.md checkboxes using planfile
- `--sync-planfile`: Store tickets in .planfile/ and sync with markdown
- `--export-yaml`: Export to planfile YAML format
- `--output, -o PATH`: Output file for YAML export
- `--koru-aware`: Enable koru integration schema for smart task planning

**Examples:**
```bash
# Generate and display tickets
lane tickets .

# Sync to TODO.md
lane tickets . --sync-todo

# Export to planfile YAML
lane tickets . --export-yaml --output strategy.yaml

# Koru-aware planning (generates tasks referencing koru operations)
lane tickets . --koru-aware --sync-planfile
```

**Note:** This feature requires the planfile package. It will be auto-installed if missing.

## Configuration

All settings are read from environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | API key for OpenRouter (preferred) |
| `OPENAI_API_KEY` | — | API key for OpenAI-compatible endpoint |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model name |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` | API base URL |
| `LLM_TIMEOUT` | `60` | HTTP timeout in seconds |
| `LLM_MAX_RETRIES` | `3` | Number of retry attempts on network error |
| `MAX_COMMITS` | `30` | How many recent commits to read |

## Runtime dependencies

- `pydantic>=2`
- `pydantic-settings>=2`
- `typer>=0.12`
- `rich>=13`
- `httpx>=0.27`
- `tenacity>=8`

## Examples

### Generate a plan for a Python project
```bash
export OPENROUTER_API_KEY="your-api-key"
lane plan /path/to/project --extra-context "Focus on improving test coverage"
```

### Use a custom model
```bash
lane plan . --model "openrouter/anthropic/claude-3.5-sonnet"
```

### Inspect what data is sent to the LLM
```bash
lane print-prompt . --extra-context "Review security issues"
```

### Generate a plan and save as JSON
```bash
lane plan . --json > plan.json
lane validate plan.json
```

### Analyze a project with limited git history
```bash
lane plan . --max-commits 10
```

### Quick auto mode (analyze + generate + sync)

```bash
# One command to analyze project and create tickets in planfile
lane auto

# With custom focus
lane auto . -e "Refactor authentication system"
```

### Code metrics analysis

```bash
# Full metrics report
lane metrics .

# High coupling files
lane metrics . --top 10 --min-coupling 0.6
```

### Koru-aware planning

```bash
lane tickets . --koru-aware --sync-planfile
```

## Architecture

### Modules

- **lane.project_analyzer** — Project analysis (manifests, structure, stack)
- **lane.git_reader** — Git history analysis
- **lane.metrics** — Code metrics (complexity, coupling, hotspots)
- **lane.koru_context** — Koru framework integration
- **lane.planner** — Orchestrates analysis → LLM → TaskPlan
- **lane.providers** — Pluggable LLM backends
- **lane.ticket_generator** — Planfile integration

## Development

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m unittest discover -s tests -v
```


## Changelog

### 0.2.x
- **Added** `lane auto` command — one-command workflow (analyze + generate + sync)
- **Added** `lane metrics` command (complexity, coupling, hotspots, bus factor)
- **Added** `--koru-aware` flag for koru-integrated planning
- **Added** `lane.metrics` module
- **Added** `lane.koru_context` module
- **Improved** Test coverage to 97%
- **Improved** Refactored CC hotspots

## License

Licensed under Apache-2.0.
