# nxdo architecture seam (PLF-138)

The `src/nxdo` package is split into five layers. The seam is enforced by
`scripts/check_import_layers.py`, which runs as a CI gate (see
[ci.yml](../.github/workflows/ci.yml)). Later per-function refactoring tickets
(PLF-108..PLF-130) must keep every import within these rules so the single
refactor-together coupling cluster found by the 2026-09-19 discovery pass
does not re-form.

## Layers

Imports may point at the **same layer or lower**. Upward imports are forbidden,
which also makes import cycles impossible by construction.

| Layer | Modules | Role |
|-------|---------|------|
| L0 foundation | `config`, `koru_context`, `text_builder` | Leaf helpers with no internal imports. |
| L1 domain | `models` | Pydantic data models (`Task`, `TaskPlan`). |
| L2 adapters | `git_reader`, `project_analyzer`, `metrics`, `metrics.*`, `providers`, `providers.*`, `llm_client`, `output`, `ticket_generator` | Collectors, renderers and provider adapters; pure consumers of L0/L1. |
| L3 orchestration | `planner` | Composes analyzer + git + providers into a plan. |
| L4 entry | `cli`, `__main__`, package `__init__` | CLI commands and the public facade; may import anything. |

Current sanctioned cross-layer edges (all downward): `models -> text_builder`;
`git_reader`/`project_analyzer -> text_builder`; `output`/`ticket_generator`/
`providers.base -> models`; `planner -> config/git_reader/llm_client/models/
project_analyzer/providers/koru_context (lazy)`; `cli -> everything below`.
`llm_client` is a backwards-compatibility shim and may import `providers.*`
(same layer), including `providers.openai_compat`.

## Import style rule

Internal imports inside `src/nxdo` must use the **relative** form
(`from .models import Task`), never absolute `from nxdo.models import Task`.
Mixed styles made the directory-level coupling analysis count `src.nxdo` and
`nxdo` as two separate clusters (11 phantom cross-cluster edges), which is
what inflated the `fan-out=19` smell.

## Running the check

```sh
python scripts/check_import_layers.py
```

The check is AST-based (stdlib only) and also inspects lazy imports inside
function bodies. When you add a module to `src/nxdo`, add it to the `LAYERS`
map in the script at the right layer.

## Fan-out smell status

The `src.nxdo/ fan-out=19 -> split needed` smell from
`project/analysis.toon.yaml` (2026-09-19) is addressed as follows:

- Removed: the 11-edge `src.nxdo -> nxdo` cluster artifact caused by absolute
  imports (unified to relative form in this seam; enforced by the style rule).
- Waived with rationale: the residual directory-level fan-out
  (`examples`=6, `nxdo.metrics`=2) comes from prompt-text references to
  `examples/` outputs and the top-layer `cli -> metrics` lazy imports. Both are
  sanctioned by the layer table above — `cli` is L4 and may import any lower
  layer — so further reduction would add indirection without reducing real
  coupling. The seam keeps per-module fan-out structurally bounded going
  forward.
