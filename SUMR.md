# lane

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `lane`
- **version**: `0.2.2`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: lane;
  version: 0.2.2;
}

dependencies {
  runtime: "pydantic>=2, pydantic-settings>=2, typer>=0.12, rich>=13, httpx>=0.27, tenacity>=8";
  dev: "pytest, pytest-mock, ruff, mypy, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

entity[name="Task"] {
  number: int!;
  title: string!;
  description: string!;
  priority: Priority!;
  task_type: TaskType!;
  estimated_hours: float;
  acceptance_criteria: list[str]!;
  dependencies: list[int]!;
}

entity[name="TaskPlan"] {
  project_name: string!;
  summary: string!;
  tasks: list[Task]!;
  generated_at: string!;
  model_used: string!;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="lane"] {

}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.10;
}
```

## Dependencies

### Runtime

```text markpact:deps python
pydantic>=2
pydantic-settings>=2
typer>=0.12
rich>=13
httpx>=0.27
tenacity>=8
```

### Development

```text markpact:deps python scope=dev
pytest
pytest-mock
ruff
mypy
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*21 nodes · 23 edges · 7 modules · CC̄=3.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_parse_response` *(in src.lane.providers.openai_compat)* | 7 | 2 | 32 | **34** |
| `read_git_context` *(in src.lane.git_reader)* | 9 | 4 | 16 | **20** |
| `cmd_plan` *(in src.lane.cli)* | 4 | 0 | 16 | **16** |
| `_build_tree` *(in src.lane.project_analyzer)* | 11 ⚠ | 2 | 13 | **15** |
| `analyze_project` *(in src.lane.project_analyzer)* | 9 | 4 | 11 | **15** |
| `cmd_print_context` *(in src.lane.cli)* | 2 | 0 | 14 | **14** |
| `cmd_print_prompt` *(in src.lane.cli)* | 1 | 0 | 13 | **13** |
| `_parse_commits` *(in src.lane.git_reader)* | 8 | 1 | 10 | **11** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/lane
# generated in 0.02s
# nodes: 21 | edges: 23 | modules: 7
# CC̄=3.7

HUBS[20]:
  src.lane.providers.openai_compat._parse_response
    CC=7  in:2  out:32  total:34
  src.lane.git_reader.read_git_context
    CC=9  in:4  out:16  total:20
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.project_analyzer._build_tree
    CC=11  in:2  out:13  total:15
  src.lane.project_analyzer.analyze_project
    CC=9  in:4  out:11  total:15
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader._parse_commits
    CC=8  in:1  out:10  total:11
  src.lane.planner.generate_next_tasks
    CC=3  in:2  out:8  total:10
  src.lane.project_analyzer._parse_pyproject
    CC=6  in:1  out:9  total:10
  src.lane.git_reader._run
    CC=3  in:6  out:2  total:8
  src.lane.project_analyzer._detect_stack
    CC=6  in:1  out:6  total:7
  src.lane.project_analyzer._parse_cargo
    CC=3  in:1  out:4  total:5
  src.lane.config.get_settings
    CC=2  in:4  out:1  total:5
  src.lane.llm_client.build_user_prompt
    CC=2  in:4  out:1  total:5
  src.lane.project_analyzer._parse_package_json
    CC=2  in:1  out:4  total:5
  src.lane.git_reader._is_git_repo
    CC=1  in:1  out:2  total:3
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan
    CC=1  in:0  out:2  total:2
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__
    CC=5  in:0  out:2  total:2
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan
    CC=1  in:0  out:2  total:2

MODULES:
  src.lane.cli  [3 funcs]
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [4 funcs]
    _is_git_repo  CC=1  out:2
    _parse_commits  CC=8  out:10
    _run  CC=3  out:2
    read_git_context  CC=9  out:16
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=2  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=3  out:8
  src.lane.project_analyzer  [6 funcs]
    _build_tree  CC=11  out:13
    _detect_stack  CC=6  out:6
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
    _parse_pyproject  CC=6  out:9
    analyze_project  CC=9  out:11
  src.lane.providers.openai_compat  [3 funcs]
    __init__  CC=5  out:2
    generate_plan  CC=1  out:2
    _parse_response  CC=7  out:32

EDGES:
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_prompt → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.llm_client.build_user_prompt
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._parse_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._detect_stack
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_pyproject
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_package_json
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._build_tree
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_cargo
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__ → src.lane.config.get_settings
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan → src.lane.providers.openai_compat._parse_response
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/lane
# generated in 0.02s
# nodes: 21 | edges: 23 | modules: 7
# CC̄=3.7

HUBS[20]:
  src.lane.providers.openai_compat._parse_response
    CC=7  in:2  out:32  total:34
  src.lane.git_reader.read_git_context
    CC=9  in:4  out:16  total:20
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.project_analyzer._build_tree
    CC=11  in:2  out:13  total:15
  src.lane.project_analyzer.analyze_project
    CC=9  in:4  out:11  total:15
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader._parse_commits
    CC=8  in:1  out:10  total:11
  src.lane.planner.generate_next_tasks
    CC=3  in:2  out:8  total:10
  src.lane.project_analyzer._parse_pyproject
    CC=6  in:1  out:9  total:10
  src.lane.git_reader._run
    CC=3  in:6  out:2  total:8
  src.lane.project_analyzer._detect_stack
    CC=6  in:1  out:6  total:7
  src.lane.project_analyzer._parse_cargo
    CC=3  in:1  out:4  total:5
  src.lane.config.get_settings
    CC=2  in:4  out:1  total:5
  src.lane.llm_client.build_user_prompt
    CC=2  in:4  out:1  total:5
  src.lane.project_analyzer._parse_package_json
    CC=2  in:1  out:4  total:5
  src.lane.git_reader._is_git_repo
    CC=1  in:1  out:2  total:3
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan
    CC=1  in:0  out:2  total:2
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__
    CC=5  in:0  out:2  total:2
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan
    CC=1  in:0  out:2  total:2

MODULES:
  src.lane.cli  [3 funcs]
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [4 funcs]
    _is_git_repo  CC=1  out:2
    _parse_commits  CC=8  out:10
    _run  CC=3  out:2
    read_git_context  CC=9  out:16
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=2  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=3  out:8
  src.lane.project_analyzer  [6 funcs]
    _build_tree  CC=11  out:13
    _detect_stack  CC=6  out:6
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
    _parse_pyproject  CC=6  out:9
    analyze_project  CC=9  out:11
  src.lane.providers.openai_compat  [3 funcs]
    __init__  CC=5  out:2
    generate_plan  CC=1  out:2
    _parse_response  CC=7  out:32

EDGES:
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_prompt → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.llm_client.build_user_prompt
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._parse_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._detect_stack
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_pyproject
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_package_json
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._build_tree
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._parse_cargo
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__ → src.lane.config.get_settings
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan → src.lane.providers.openai_compat._parse_response
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 17f 1689L | python:13,shell:2,yaml:1,toml:1 | 2026-05-26
# generated in 0.01s
# CC̅=3.7 | critical:0/38 | dups:0 | cycles:1

HEALTH[0]: ok

REFACTOR[1]:
  1. break 1 circular dependencies

PIPELINES[19]:
  [1] Src [cmd_plan]: cmd_plan → get_settings
      PURITY: 100% pure
  [2] Src [cmd_print_context]: cmd_print_context → analyze_project → _detect_stack
      PURITY: 100% pure
  [3] Src [cmd_print_prompt]: cmd_print_prompt → analyze_project → _detect_stack
      PURITY: 100% pure
  [4] Src [cmd_validate]: cmd_validate
      PURITY: 100% pure
  [5] Src [app_entry]: app_entry
      PURITY: 100% pure
  [6] Src [main]: main → get_settings
      PURITY: 100% pure
  [7] Src [__str__]: __str__
      PURITY: 100% pure
  [8] Src [to_text]: to_text
      PURITY: 100% pure
  [9] Src [parse_task_plan_response]: parse_task_plan_response → _parse_response
      PURITY: 100% pure
  [10] Src [__init__]: __init__
      PURITY: 100% pure
  [11] Src [generate_task_plan]: generate_task_plan → build_user_prompt
      PURITY: 100% pure
  [12] Src [to_text]: to_text
      PURITY: 100% pure
  [13] Src [__str__]: __str__
      PURITY: 100% pure
  [14] Src [to_dict]: to_dict
      PURITY: 100% pure
  [15] Src [__str__]: __str__
      PURITY: 100% pure
  [16] Src [to_dict]: to_dict
      PURITY: 100% pure
  [17] Src [__init__]: __init__ → get_settings
      PURITY: 100% pure
  [18] Src [generate_plan]: generate_plan → _parse_response
      PURITY: 100% pure
  [19] Src [_call_api]: _call_api
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=3.7    ←in:0  →out:0
  │ project_analyzer           191L  1C    8m  CC=11     ←2
  │ cli                        160L  0C    6m  CC=4      ←0
  │ git_reader                 152L  2C    6m  CC=9      ←2
  │ openai_compat              152L  1C    4m  CC=7      ←1
  │ models                      90L  4C    4m  CC=7      ←0
  │ llm_client                  77L  1C    4m  CC=3      ←2
  │ output                      67L  0C    3m  CC=4      ←1
  │ config                      42L  1C    1m  CC=2      ←3
  │ planner                     42L  0C    1m  CC=3      ←1
  │ __init__                    31L  0C    0m  CC=0.0    ←0
  │ base                        19L  1C    1m  CC=1      ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              93L  0C    0m  CC=0.0    ←0
  │ project.sh                  48L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 13f 1035L | 2026-05-26

SUMMARY:
  files_scanned: 13
  total_lines:   1035
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       4705
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 38 func | 10f | 2026-05-26
# generated in 0.00s

NEXT[1] (ranked by impact):
  [1] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.7 → ≤2.6
  max-CC:      11 → ≤5
  god-modules: 1 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

## Intent

Generate the next 10 project tasks from project state, git history and an LLM prompt.
