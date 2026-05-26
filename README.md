# lane


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.2.6-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.93-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.6h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.9342 (9 commits)
- 👤 **Human dev:** ~$357 (3.6h @ $100/h, 30min dedup)

Generated on 2026-05-26 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

`lane` is a Python package that inspects the current project state, reads recent git history, adds a user question for an LLM, and returns a concrete plan for the next 10 engineering tasks.

## What is included

- **Project snapshot analysis** — README, manifests (pyproject.toml, package.json, Cargo.toml, …), directory tree, stack detection
- **Git context** — recent commits, most-changed files, TODO/FIXME markers
- **Pydantic models** — validated data models for tasks and plans (`Task`, `TaskPlan`)
- **Provider abstraction** — pluggable LLM backends; ships with an OpenAI-compatible provider (works with OpenRouter and any OpenAI-style API)
- **Planner orchestrator** — `generate_next_tasks()` composes analysis + prompt + LLM call into a validated TaskPlan
- **Rich CLI** — `lane plan`, `lane print-context`, `lane print-prompt`, `lane validate`
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

## Development

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m unittest discover -s tests -v
```


## License

Licensed under Apache-2.0.
