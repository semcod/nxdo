# lane

`lane` is a Python package that inspects the current project state, reads recent git history, adds a user question for an LLM, and returns a concrete plan for the next 10 engineering tasks.

## What is included

- project snapshot analysis (`README`, manifests, directory tree, stack detection)
- recent git context (`git log`, changed files, TODO/FIXME markers)
- data models for 10-task plans
- an OpenAI-compatible LLM client suitable for OpenRouter-style APIs
- a small CLI: `python -m lane --print-prompt` or `lane`

## Suggested libraries

The current implementation keeps dependencies minimal and uses the Python standard library. If you want to extend `lane`, these libraries are good candidates:

- `httpx` — richer HTTP client for LLM providers
- `pydantic` — stronger validation for plan schemas
- `typer` — more ergonomic CLI
- `GitPython` — higher-level git access if you want to avoid subprocess calls
- `jinja2` — templating for prompt generation and plan exports

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
python -m lane --print-prompt
```

To generate a real plan, set `OPENROUTER_API_KEY` or `OPENAI_API_KEY` and run:

```bash
lane --extra-context "What should we build next for this repository?"
```