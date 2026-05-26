# lane

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

## Development

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m unittest discover -s tests -v
```
