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
- **version**: `0.2.7`
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
  version: 0.2.7;
}

dependencies {
  runtime: "pydantic>=2, pydantic-settings>=2, typer>=0.12, rich>=13, httpx>=0.27, tenacity>=8, pyyaml>=6.0, planfile @ file:///home/tom/github/semcod/planfile";
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
pyyaml>=6.0
planfile @ file:///home/tom/github/semcod/planfile
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

*54 nodes · 58 edges · 8 modules · CC̄=2.7*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `cmd_tickets` *(in src.lane.cli)* | 9 | 0 | 32 | **32** |
| `_build_tree` *(in src.lane.project_analyzer)* | 8 | 2 | 14 | **16** |
| `_create_task_from_dict` *(in src.lane.providers.openai_compat)* | 2 | 1 | 15 | **16** |
| `cmd_plan` *(in src.lane.cli)* | 4 | 0 | 16 | **16** |
| `cmd_print_context` *(in src.lane.cli)* | 2 | 0 | 14 | **14** |
| `cmd_print_prompt` *(in src.lane.cli)* | 1 | 0 | 13 | **13** |
| `read_git_context` *(in src.lane.git_reader)* | 2 | 4 | 8 | **12** |
| `generate_next_tasks` *(in src.lane.planner)* | 3 | 3 | 8 | **11** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/lane
# generated in 0.02s
# nodes: 54 | edges: 58 | modules: 8
# CC̄=2.7

HUBS[20]:
  src.lane.cli.cmd_tickets
    CC=9  in:0  out:32  total:32
  src.lane.project_analyzer._build_tree
    CC=8  in:2  out:14  total:16
  src.lane.providers.openai_compat._create_task_from_dict
    CC=2  in:1  out:15  total:16
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader.read_git_context
    CC=2  in:4  out:8  total:12
  src.lane.planner.generate_next_tasks
    CC=3  in:3  out:8  total:11
  src.lane.providers.openai_compat._parse_response
    CC=1  in:2  out:8  total:10
  src.lane.git_reader._parse_commits
    CC=7  in:1  out:9  total:10
  src.lane.project_analyzer.analyze_project
    CC=1  in:4  out:5  total:9
  src.lane.ticket_generator.sync_to_todo_md
    CC=3  in:1  out:6  total:7
  src.lane.git_reader._run
    CC=3  in:5  out:2  total:7
  src.lane.config.get_settings
    CC=2  in:5  out:1  total:6
  src.lane.project_analyzer._parse_pyproject_tomllib
    CC=4  in:1  out:5  total:6
  src.lane.providers.openai_compat._parse_json_response
    CC=3  in:1  out:5  total:6
  src.lane.project_analyzer._resolve_name_and_description
    CC=3  in:1  out:5  total:6
  src.lane.project_analyzer._parse_cargo
    CC=3  in:1  out:4  total:5
  src.lane.ticket_generator._map_priority
    CC=1  in:3  out:2  total:5
  src.lane.project_analyzer._parse_pyproject_regex
    CC=3  in:1  out:4  total:5

MODULES:
  src.lane.cli  [4 funcs]
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
    cmd_tickets  CC=9  out:32
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [15 funcs]
    _count_file_frequencies  CC=3  out:3
    _create_commit_info  CC=1  out:1
    _create_empty_context  CC=1  out:1
    _format_file_summary  CC=2  out:2
    _get_file_frequency  CC=1  out:3
    _get_git_branch  CC=1  out:1
    _get_git_commits  CC=1  out:2
    _get_git_remote  CC=1  out:1
    _get_git_todos  CC=3  out:3
    _is_git_repo  CC=1  out:2
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=2  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=3  out:8
  src.lane.project_analyzer  [18 funcs]
    _build_tree  CC=8  out:14
    _check_pattern_match  CC=2  out:3
    _collect_file_contents  CC=4  out:3
    _detect_stack  CC=4  out:4
    _get_connector  CC=1  out:1
    _get_extension  CC=1  out:1
    _get_tree_symbol  CC=4  out:0
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
    _parse_pyproject  CC=2  out:2
  src.lane.providers.openai_compat  [7 funcs]
    __init__  CC=5  out:2
    generate_plan  CC=1  out:2
    _create_task_from_dict  CC=2  out:15
    _parse_json_response  CC=3  out:5
    _parse_response  CC=1  out:8
    _parse_tasks_from_data  CC=2  out:4
    _strip_markdown_fences  CC=3  out:4
  src.lane.ticket_generator  [5 funcs]
    _create_temp_strategy  CC=2  out:3
    _map_priority  CC=1  out:2
    export_to_planfile_yaml  CC=3  out:4
    sync_to_todo_md  CC=3  out:6
    task_plan_to_tickets  CC=3  out:2

EDGES:
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader._run_git_command → src.lane.git_reader._run
  src.lane.git_reader._get_git_branch → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_remote → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_commits → src.lane.git_reader._run
  src.lane.git_reader._get_git_commits → src.lane.git_reader._parse_commits
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._run
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._count_file_frequencies
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._format_file_summary
  src.lane.git_reader._get_git_todos → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_branch
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_remote
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_file_frequency
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_todos
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.git_reader.read_git_context → src.lane.git_reader._create_empty_context
  src.lane.git_reader._parse_commits → src.lane.git_reader._parse_commit_metadata
  src.lane.git_reader._parse_commits → src.lane.git_reader._create_commit_info
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.project_analyzer._collect_file_contents → src.lane.project_analyzer._read_file_safely
  src.lane.project_analyzer._collect_file_contents → src.lane.project_analyzer._truncate_file_content
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_pyproject
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_package_json
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_cargo
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._readme_summary
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._collect_file_contents
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._detect_stack
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._resolve_name_and_description
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._build_tree
  src.lane.project_analyzer._detect_stack → src.lane.project_analyzer._check_pattern_match
  src.lane.project_analyzer._parse_pyproject → src.lane.project_analyzer._parse_pyproject_tomllib
  src.lane.project_analyzer._parse_pyproject → src.lane.project_analyzer._parse_pyproject_regex
  src.lane.project_analyzer._get_connector → src.lane.project_analyzer._get_tree_symbol
  src.lane.project_analyzer._get_extension → src.lane.project_analyzer._get_tree_symbol
  src.lane.project_analyzer._build_tree → src.lane.project_analyzer._should_ignore_entry
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__ → src.lane.config.get_settings
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan → src.lane.providers.openai_compat._parse_response
  src.lane.providers.openai_compat._parse_tasks_from_data → src.lane.providers.openai_compat._create_task_from_dict
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._strip_markdown_fences
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._parse_json_response
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._parse_tasks_from_data
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
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
# nodes: 54 | edges: 58 | modules: 8
# CC̄=2.7

HUBS[20]:
  src.lane.cli.cmd_tickets
    CC=9  in:0  out:32  total:32
  src.lane.project_analyzer._build_tree
    CC=8  in:2  out:14  total:16
  src.lane.providers.openai_compat._create_task_from_dict
    CC=2  in:1  out:15  total:16
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader.read_git_context
    CC=2  in:4  out:8  total:12
  src.lane.planner.generate_next_tasks
    CC=3  in:3  out:8  total:11
  src.lane.providers.openai_compat._parse_response
    CC=1  in:2  out:8  total:10
  src.lane.git_reader._parse_commits
    CC=7  in:1  out:9  total:10
  src.lane.project_analyzer.analyze_project
    CC=1  in:4  out:5  total:9
  src.lane.ticket_generator.sync_to_todo_md
    CC=3  in:1  out:6  total:7
  src.lane.git_reader._run
    CC=3  in:5  out:2  total:7
  src.lane.config.get_settings
    CC=2  in:5  out:1  total:6
  src.lane.project_analyzer._parse_pyproject_tomllib
    CC=4  in:1  out:5  total:6
  src.lane.providers.openai_compat._parse_json_response
    CC=3  in:1  out:5  total:6
  src.lane.project_analyzer._resolve_name_and_description
    CC=3  in:1  out:5  total:6
  src.lane.project_analyzer._parse_cargo
    CC=3  in:1  out:4  total:5
  src.lane.ticket_generator._map_priority
    CC=1  in:3  out:2  total:5
  src.lane.project_analyzer._parse_pyproject_regex
    CC=3  in:1  out:4  total:5

MODULES:
  src.lane.cli  [4 funcs]
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
    cmd_tickets  CC=9  out:32
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [15 funcs]
    _count_file_frequencies  CC=3  out:3
    _create_commit_info  CC=1  out:1
    _create_empty_context  CC=1  out:1
    _format_file_summary  CC=2  out:2
    _get_file_frequency  CC=1  out:3
    _get_git_branch  CC=1  out:1
    _get_git_commits  CC=1  out:2
    _get_git_remote  CC=1  out:1
    _get_git_todos  CC=3  out:3
    _is_git_repo  CC=1  out:2
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=2  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=3  out:8
  src.lane.project_analyzer  [18 funcs]
    _build_tree  CC=8  out:14
    _check_pattern_match  CC=2  out:3
    _collect_file_contents  CC=4  out:3
    _detect_stack  CC=4  out:4
    _get_connector  CC=1  out:1
    _get_extension  CC=1  out:1
    _get_tree_symbol  CC=4  out:0
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
    _parse_pyproject  CC=2  out:2
  src.lane.providers.openai_compat  [7 funcs]
    __init__  CC=5  out:2
    generate_plan  CC=1  out:2
    _create_task_from_dict  CC=2  out:15
    _parse_json_response  CC=3  out:5
    _parse_response  CC=1  out:8
    _parse_tasks_from_data  CC=2  out:4
    _strip_markdown_fences  CC=3  out:4
  src.lane.ticket_generator  [5 funcs]
    _create_temp_strategy  CC=2  out:3
    _map_priority  CC=1  out:2
    export_to_planfile_yaml  CC=3  out:4
    sync_to_todo_md  CC=3  out:6
    task_plan_to_tickets  CC=3  out:2

EDGES:
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader._run_git_command → src.lane.git_reader._run
  src.lane.git_reader._get_git_branch → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_remote → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_commits → src.lane.git_reader._run
  src.lane.git_reader._get_git_commits → src.lane.git_reader._parse_commits
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._run
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._count_file_frequencies
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._format_file_summary
  src.lane.git_reader._get_git_todos → src.lane.git_reader._run
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_branch
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_remote
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_file_frequency
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_todos
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.git_reader.read_git_context → src.lane.git_reader._create_empty_context
  src.lane.git_reader._parse_commits → src.lane.git_reader._parse_commit_metadata
  src.lane.git_reader._parse_commits → src.lane.git_reader._create_commit_info
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.project_analyzer._collect_file_contents → src.lane.project_analyzer._read_file_safely
  src.lane.project_analyzer._collect_file_contents → src.lane.project_analyzer._truncate_file_content
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_pyproject
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_package_json
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._parse_cargo
  src.lane.project_analyzer._resolve_name_and_description → src.lane.project_analyzer._readme_summary
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._collect_file_contents
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._detect_stack
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._resolve_name_and_description
  src.lane.project_analyzer.analyze_project → src.lane.project_analyzer._build_tree
  src.lane.project_analyzer._detect_stack → src.lane.project_analyzer._check_pattern_match
  src.lane.project_analyzer._parse_pyproject → src.lane.project_analyzer._parse_pyproject_tomllib
  src.lane.project_analyzer._parse_pyproject → src.lane.project_analyzer._parse_pyproject_regex
  src.lane.project_analyzer._get_connector → src.lane.project_analyzer._get_tree_symbol
  src.lane.project_analyzer._get_extension → src.lane.project_analyzer._get_tree_symbol
  src.lane.project_analyzer._build_tree → src.lane.project_analyzer._should_ignore_entry
  src.lane.providers.openai_compat.OpenAICompatProvider.__init__ → src.lane.config.get_settings
  src.lane.providers.openai_compat.OpenAICompatProvider.generate_plan → src.lane.providers.openai_compat._parse_response
  src.lane.providers.openai_compat._parse_tasks_from_data → src.lane.providers.openai_compat._create_task_from_dict
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._strip_markdown_fences
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._parse_json_response
  src.lane.providers.openai_compat._parse_response → src.lane.providers.openai_compat._parse_tasks_from_data
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 20f 2141L | python:14,yaml:3,txt:1,shell:1,toml:1 | 2026-05-26
# generated in 0.00s
# CC̅=2.7 | critical:0/70 | dups:0 | cycles:1

HEALTH[0]: ok

REFACTOR[1]:
  1. break 1 circular dependencies

PIPELINES[20]:
  [1] Src [__str__]: __str__
      PURITY: 100% pure
  [2] Src [to_text]: to_text
      PURITY: 100% pure
  [3] Src [parse_task_plan_response]: parse_task_plan_response → _parse_response → _strip_markdown_fences
      PURITY: 100% pure
  [4] Src [__init__]: __init__
      PURITY: 100% pure
  [5] Src [generate_task_plan]: generate_task_plan → build_user_prompt
      PURITY: 100% pure
  [6] Src [to_text]: to_text
      PURITY: 100% pure
  [7] Src [__str__]: __str__
      PURITY: 100% pure
  [8] Src [to_dict]: to_dict
      PURITY: 100% pure
  [9] Src [__str__]: __str__
      PURITY: 100% pure
  [10] Src [to_dict]: to_dict
      PURITY: 100% pure
  [11] Src [__init__]: __init__ → get_settings
      PURITY: 100% pure
  [12] Src [generate_plan]: generate_plan → _parse_response → _strip_markdown_fences
      PURITY: 100% pure
  [13] Src [_call_api]: _call_api
      PURITY: 100% pure
  [14] Src [cmd_plan]: cmd_plan → get_settings
      PURITY: 100% pure
  [15] Src [cmd_print_context]: cmd_print_context → analyze_project → _collect_file_contents → _read_file_safely
      PURITY: 100% pure
  [16] Src [cmd_print_prompt]: cmd_print_prompt → analyze_project → _collect_file_contents → _read_file_safely
      PURITY: 100% pure
  [17] Src [cmd_validate]: cmd_validate
      PURITY: 100% pure
  [18] Src [cmd_tickets]: cmd_tickets → get_settings
      PURITY: 100% pure
  [19] Src [app_entry]: app_entry
      PURITY: 100% pure
  [20] Src [main]: main → get_settings
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=2.7    ←in:0  →out:0
  │ project_analyzer           258L  1C   19m  CC=8      ←2
  │ cli                        216L  0C    7m  CC=9      ←0
  │ git_reader                 207L  2C   17m  CC=7      ←2
  │ openai_compat              172L  1C    8m  CC=5      ←1
  │ ticket_generator           165L  0C    5m  CC=3      ←1
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
  │ pyproject.toml              98L  0C    0m  CC=0.0    ←0
  │ tree.txt                    55L  0C    0m  CC=0.0    ←0
  │ project.sh                  48L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    10L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 14f 1398L | 2026-05-26

SUMMARY:
  files_scanned: 14
  total_lines:   1398
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   6
  scan_ms:       3715

HOTSPOTS[2] (files with most duplication):
  src/lane/git_reader.py  dup=6L  groups=1  frags=2  (0.4%)
  src/lane/project_analyzer.py  dup=6L  groups=1  frags=2  (0.4%)

DUPLICATES[2] (ranked by impact):
  [398e7fc98c20a6ea]   STRU  _get_git_branch  L=3 N=2 saved=3 sim=1.00
      src/lane/git_reader.py:82-84  (_get_git_branch)
      src/lane/git_reader.py:87-89  (_get_git_remote)
  [dba932c7fb158cc5]   STRU  _get_connector  L=3 N=2 saved=3 sim=1.00
      src/lane/project_analyzer.py:229-231  (_get_connector)
      src/lane/project_analyzer.py:234-236  (_get_extension)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → src/lane/utils/_get_git_branch.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: src/lane/git_reader.py
  [2] ○ extract_function   → src/lane/utils/_get_connector.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: src/lane/project_analyzer.py

EFFORT_ESTIMATE (total ≈ 0.2h):
  easy   _get_git_branch                     saved=3L  ~6min
  easy   _get_connector                      saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 6 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 70 func | 11f | 2026-05-26
# generated in 0.00s

NEXT[1] (ranked by impact):
  [1] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          2.7 → ≤1.9
  max-CC:      9 → ≤4
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
  prev CC̄=2.6 → now CC̄=2.7
```

## Intent

Generate the next 10 project tasks from project state, git history and an LLM prompt.
