# Planfile integration

nxdo can write generated tickets straight into a repo-local [planfile](https://pypi.org/project/planfile/) store, so analysis output becomes an executable backlog instead of a report that rots in the terminal.

## What it does

| Flag | Effect |
|------|--------|
| `--sync-planfile` | Creates/updates `.planfile/` in the target repo and writes each generated task as a ticket |
| `--export-yaml` | Writes the task plan to a planfile-compatible YAML file (`strategy.yaml` by default) |
| `--sync-todo` | Appends tasks to `TODO.md` inside a managed `<!-- nxdo:generated-tasks -->` block (idempotent; manual content preserved) |
| `--koru-aware` | Reads open planfile tickets first, so generated work does not duplicate in-flight items |

## Typical flow

```bash
# 1. Analyze the repo and store tickets in its own .planfile store
nxdo tickets . --koru-aware --sync-planfile

# 2. Inspect what landed
planfile ticket list --status open

# 3. Let the queue execute them (koru) or work them by hand
```

`--koru-aware` first reads the repo's existing tickets; `--sync-planfile` then writes only new work. Running it twice does not duplicate tickets.

## How tickets land

Each generated task becomes a ticket with `source.tool: nxdo`, a dedupe key derived from the task title, and the priority nxdo assigned. Tickets are written to the target repository's own `.planfile/` store — never to a parent directory's store.

## Benefits

- **No copy-paste**: analysis → backlog in one command
- **Deduplication**: `--koru-aware` plus dedupe keys keep the queue clean across repeated scans
- **Idempotent**: re-running after refactors only adds genuinely new work
- **Interop**: the store is plain planfile YAML — `planfile`, `koru queue`, and GitHub sync all work on it unchanged

## Troubleshooting

- `planfile not available` — install `planfile` into the same environment (`pip install planfile`) or export with `--export-yaml` and import later.
- Tickets appear in the wrong repo — always pass the target repo path (`nxdo tickets /path/to/repo ...`); the store is created relative to that path.
