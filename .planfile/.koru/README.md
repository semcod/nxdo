# `.planfile/.koru/` — koru runtime artefacts

This directory is owned by **koru** (not planfile). It contains
non-authoritative runtime by-products of `koru --queue` runs:

- `runs/` — one log file per queue run, named
  `queue-<UTC-timestamp>-<pid>.log`. Useful for postmortems but **safe
  to delete at any time** — planfile sprint YAML is the source of truth.
- `prompts/` — captured human prompts and answers (when koru is run
  with `--interactive`). These mirror what is also recorded in the
  ticket via `planfile ticket done` (see also the planfile lifecycle docs).
- `llm-cache/` — opt-in cache for `executor.kind=llm` responses.

**Gitignored by default.** Add `.planfile/.koru/` to `.gitignore`
unless you want to share run history across collaborators.

koru never writes outside `.planfile/`. If you find koru artefacts
in `/tmp/` or anywhere else, that's a bug — please report it.
