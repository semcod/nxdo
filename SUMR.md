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
- **version**: `0.2.19`
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
  version: 0.2.19;
}

dependencies {
  runtime: "pydantic>=2, pydantic-settings>=2, typer>=0.12, rich>=13, httpx>=0.27, tenacity>=8, pyyaml>=6.0, planfile @ git+https://github.com/semcod/planfile.git";
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
planfile @ git+https://github.com/semcod/planfile.git
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

*92 nodes · 96 edges · 12 modules · CC̄=4.0*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `cmd_auto` *(in src.lane.cli)* | 9 | 0 | 33 | **33** |
| `cmd_metrics` *(in src.lane.cli)* | 11 ⚠ | 0 | 33 | **33** |
| `_create_task_from_dict` *(in src.lane.providers.openai_compat)* | 6 | 1 | 20 | **21** |
| `identify_bug_hotspots` *(in src.lane.metrics.hotspots)* | 16 ⚠ | 2 | 18 | **20** |
| `_calculate_fan_in` *(in src.lane.metrics.complexity)* | 12 ⚠ | 1 | 17 | **18** |
| `collect_file_metrics` *(in src.lane.metrics.complexity)* | 8 | 2 | 16 | **18** |
| `_format_project_state_for_llm` *(in src.lane.koru_context)* | 7 | 1 | 16 | **17** |
| `calculate_bus_factor` *(in src.lane.metrics.hotspots)* | 14 ⚠ | 2 | 14 | **16** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/lane
# generated in 0.04s
# nodes: 92 | edges: 96 | modules: 12
# CC̄=4.0

HUBS[20]:
  src.lane.cli.cmd_auto
    CC=9  in:0  out:33  total:33
  src.lane.cli.cmd_metrics
    CC=11  in:0  out:33  total:33
  src.lane.providers.openai_compat._create_task_from_dict
    CC=6  in:1  out:20  total:21
  src.lane.metrics.hotspots.identify_bug_hotspots
    CC=16  in:2  out:18  total:20
  src.lane.metrics.complexity._calculate_fan_in
    CC=12  in:1  out:17  total:18
  src.lane.metrics.complexity.collect_file_metrics
    CC=8  in:2  out:16  total:18
  src.lane.koru_context._format_project_state_for_llm
    CC=7  in:1  out:16  total:17
  src.lane.metrics.hotspots.calculate_bus_factor
    CC=14  in:2  out:14  total:16
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.koru_context._format_operations_for_llm
    CC=7  in:1  out:14  total:15
  src.lane.metrics.coupling.collect_coupling_matrix
    CC=18  in:1  out:13  total:14
  src.lane.metrics.hotspots._get_file_commits_with_info
    CC=14  in:1  out:13  total:14
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.project_analyzer._build_tree
    CC=6  in:2  out:12  total:14
  src.lane.metrics.coupling._get_commits_with_files
    CC=13  in:1  out:13  total:14
  src.lane.planner.generate_next_tasks
    CC=5  in:4  out:9  total:13
  src.lane.ticket_generator.sync_to_planfile
    CC=8  in:1  out:12  total:13
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader.read_git_context
    CC=2  in:4  out:8  total:12
  src.lane.providers.openai_compat.OpenAICompatProvider._call_api
    CC=5  in:0  out:12  total:12

MODULES:
  src.lane.cli  [10 funcs]
    _display_tickets  CC=3  out:5
    _export_yaml_if_requested  CC=3  out:1
    _get_priority_emoji  CC=1  out:1
    _sync_planfile_if_requested  CC=3  out:3
    _sync_todos_if_requested  CC=2  out:4
    cmd_auto  CC=9  out:33
    cmd_metrics  CC=11  out:33
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [19 funcs]
    _count_file_frequencies  CC=4  out:4
    _create_commit_info  CC=1  out:2
    _create_empty_context  CC=1  out:1
    _filter_git_paths  CC=3  out:1
    _finalize_commit  CC=2  out:2
    _format_file_summary  CC=2  out:2
    _get_file_frequency  CC=1  out:3
    _get_git_branch  CC=1  out:1
    _get_git_commits  CC=1  out:2
    _get_git_remote  CC=1  out:1
  src.lane.koru_context  [6 funcs]
    _format_operations_for_llm  CC=7  out:14
    _format_project_state_for_llm  CC=7  out:16
    _load_operations  CC=3  out:2
    _load_project_state  CC=6  out:10
    build_koru_context  CC=3  out:9
    get_koru_system_prompt_extension  CC=1  out:0
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=3  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.metrics.complexity  [6 funcs]
    _analyze_imports  CC=7  out:10
    _analyze_types  CC=14  out:6
    _calculate_cyclomatic_complexity  CC=5  out:5
    _calculate_fan_in  CC=12  out:17
    _count_lines  CC=4  out:3
    collect_file_metrics  CC=8  out:16
  src.lane.metrics.coupling  [2 funcs]
    _get_commits_with_files  CC=13  out:13
    collect_coupling_matrix  CC=18  out:13
  src.lane.metrics.hotspots  [5 funcs]
    _get_bug_fix_commits  CC=6  out:7
    _get_file_commits_with_info  CC=14  out:13
    calculate_bus_factor  CC=14  out:14
    get_critical_bus_factor_files  CC=7  out:11
    identify_bug_hotspots  CC=16  out:18
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=5  out:9
  src.lane.project_analyzer  [19 funcs]
    _build_tree  CC=6  out:12
    _check_pattern_match  CC=2  out:3
    _collect_file_contents  CC=4  out:3
    _detect_stack  CC=4  out:4
    _get_connector  CC=1  out:1
    _get_extension  CC=1  out:1
    _get_subtree_lines  CC=4  out:3
    _get_tree_symbol  CC=4  out:0
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
  src.lane.providers.openai_compat  [8 funcs]
    __init__  CC=5  out:2
    _call_api  CC=5  out:12
    generate_plan  CC=1  out:2
    _create_task_from_dict  CC=6  out:20
    _parse_json_response  CC=3  out:5
    _parse_response  CC=1  out:8
    _parse_tasks_from_data  CC=2  out:4
    _strip_markdown_fences  CC=3  out:4
  src.lane.ticket_generator  [12 funcs]
    _build_todo_section  CC=4  out:5
    _ensure_planfile_installed  CC=3  out:5
    _map_priority  CC=1  out:2
    _remove_generated_todo_sections  CC=1  out:5
    _remove_legacy_generated_todo_sections  CC=6  out:4
    _remove_managed_todo_blocks  CC=5  out:3
    _resolve_todo_path  CC=3  out:1
    _sync_todo_section  CC=2  out:6
    export_to_planfile_yaml  CC=3  out:4
    sync_to_planfile  CC=8  out:12

EDGES:
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_prompt → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.llm_client.build_user_prompt
  src.lane.cli._sync_todos_if_requested → src.lane.ticket_generator.sync_to_todo_md
  src.lane.cli._sync_planfile_if_requested → src.lane.ticket_generator.sync_to_planfile
  src.lane.cli._export_yaml_if_requested → src.lane.ticket_generator.export_to_planfile_yaml
  src.lane.cli._display_tickets → src.lane.cli._get_priority_emoji
  src.lane.cli.cmd_metrics → src.lane.metrics.complexity.collect_file_metrics
  src.lane.cli.cmd_auto → src.lane.metrics.hotspots.identify_bug_hotspots
  src.lane.cli.cmd_auto → src.lane.metrics.complexity.collect_file_metrics
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader._run_git_command → src.lane.git_reader._run
  src.lane.git_reader._get_git_branch → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_remote → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_commits → src.lane.git_reader._run
  src.lane.git_reader._get_git_commits → src.lane.git_reader._parse_commits
  src.lane.git_reader._count_file_frequencies → src.lane.git_reader._should_ignore_git_path
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._run
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._count_file_frequencies
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._format_file_summary
  src.lane.git_reader._get_git_todos → src.lane.git_reader._run
  src.lane.git_reader._get_git_todos → src.lane.git_reader._should_include_todo_line
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_branch
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_remote
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_file_frequency
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_todos
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.git_reader.read_git_context → src.lane.git_reader._create_empty_context
  src.lane.git_reader._create_commit_info → src.lane.git_reader._filter_git_paths
  src.lane.git_reader._finalize_commit → src.lane.git_reader._create_commit_info
  src.lane.git_reader._parse_commits → src.lane.git_reader._finalize_commit
  src.lane.git_reader._parse_commits → src.lane.git_reader._parse_commit_metadata
  src.lane.git_reader._filter_git_paths → src.lane.git_reader._should_ignore_git_path
  src.lane.git_reader._should_include_todo_line → src.lane.git_reader._should_ignore_git_path
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.planner.generate_next_tasks → src.lane.koru_context.build_koru_context
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.koru_context.build_koru_context → src.lane.koru_context._load_operations
  src.lane.koru_context.build_koru_context → src.lane.koru_context._format_operations_for_llm
  src.lane.koru_context.build_koru_context → src.lane.koru_context._format_project_state_for_llm
  src.lane.koru_context.build_koru_context → src.lane.koru_context._load_project_state
  src.lane.ticket_generator.task_plan_to_tickets → src.lane.ticket_generator._map_priority
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
# generated in 0.04s
# nodes: 92 | edges: 96 | modules: 12
# CC̄=4.0

HUBS[20]:
  src.lane.cli.cmd_auto
    CC=9  in:0  out:33  total:33
  src.lane.cli.cmd_metrics
    CC=11  in:0  out:33  total:33
  src.lane.providers.openai_compat._create_task_from_dict
    CC=6  in:1  out:20  total:21
  src.lane.metrics.hotspots.identify_bug_hotspots
    CC=16  in:2  out:18  total:20
  src.lane.metrics.complexity._calculate_fan_in
    CC=12  in:1  out:17  total:18
  src.lane.metrics.complexity.collect_file_metrics
    CC=8  in:2  out:16  total:18
  src.lane.koru_context._format_project_state_for_llm
    CC=7  in:1  out:16  total:17
  src.lane.metrics.hotspots.calculate_bus_factor
    CC=14  in:2  out:14  total:16
  src.lane.cli.cmd_plan
    CC=4  in:0  out:16  total:16
  src.lane.koru_context._format_operations_for_llm
    CC=7  in:1  out:14  total:15
  src.lane.metrics.coupling.collect_coupling_matrix
    CC=18  in:1  out:13  total:14
  src.lane.metrics.hotspots._get_file_commits_with_info
    CC=14  in:1  out:13  total:14
  src.lane.cli.cmd_print_context
    CC=2  in:0  out:14  total:14
  src.lane.project_analyzer._build_tree
    CC=6  in:2  out:12  total:14
  src.lane.metrics.coupling._get_commits_with_files
    CC=13  in:1  out:13  total:14
  src.lane.planner.generate_next_tasks
    CC=5  in:4  out:9  total:13
  src.lane.ticket_generator.sync_to_planfile
    CC=8  in:1  out:12  total:13
  src.lane.cli.cmd_print_prompt
    CC=1  in:0  out:13  total:13
  src.lane.git_reader.read_git_context
    CC=2  in:4  out:8  total:12
  src.lane.providers.openai_compat.OpenAICompatProvider._call_api
    CC=5  in:0  out:12  total:12

MODULES:
  src.lane.cli  [10 funcs]
    _display_tickets  CC=3  out:5
    _export_yaml_if_requested  CC=3  out:1
    _get_priority_emoji  CC=1  out:1
    _sync_planfile_if_requested  CC=3  out:3
    _sync_todos_if_requested  CC=2  out:4
    cmd_auto  CC=9  out:33
    cmd_metrics  CC=11  out:33
    cmd_plan  CC=4  out:16
    cmd_print_context  CC=2  out:14
    cmd_print_prompt  CC=1  out:13
  src.lane.config  [1 funcs]
    get_settings  CC=2  out:1
  src.lane.git_reader  [19 funcs]
    _count_file_frequencies  CC=4  out:4
    _create_commit_info  CC=1  out:2
    _create_empty_context  CC=1  out:1
    _filter_git_paths  CC=3  out:1
    _finalize_commit  CC=2  out:2
    _format_file_summary  CC=2  out:2
    _get_file_frequency  CC=1  out:3
    _get_git_branch  CC=1  out:1
    _get_git_commits  CC=1  out:2
    _get_git_remote  CC=1  out:1
  src.lane.koru_context  [6 funcs]
    _format_operations_for_llm  CC=7  out:14
    _format_project_state_for_llm  CC=7  out:16
    _load_operations  CC=3  out:2
    _load_project_state  CC=6  out:10
    build_koru_context  CC=3  out:9
    get_koru_system_prompt_extension  CC=1  out:0
  src.lane.llm_client  [3 funcs]
    generate_task_plan  CC=1  out:2
    build_user_prompt  CC=3  out:1
    parse_task_plan_response  CC=1  out:1
  src.lane.metrics.complexity  [6 funcs]
    _analyze_imports  CC=7  out:10
    _analyze_types  CC=14  out:6
    _calculate_cyclomatic_complexity  CC=5  out:5
    _calculate_fan_in  CC=12  out:17
    _count_lines  CC=4  out:3
    collect_file_metrics  CC=8  out:16
  src.lane.metrics.coupling  [2 funcs]
    _get_commits_with_files  CC=13  out:13
    collect_coupling_matrix  CC=18  out:13
  src.lane.metrics.hotspots  [5 funcs]
    _get_bug_fix_commits  CC=6  out:7
    _get_file_commits_with_info  CC=14  out:13
    calculate_bus_factor  CC=14  out:14
    get_critical_bus_factor_files  CC=7  out:11
    identify_bug_hotspots  CC=16  out:18
  src.lane.planner  [1 funcs]
    generate_next_tasks  CC=5  out:9
  src.lane.project_analyzer  [19 funcs]
    _build_tree  CC=6  out:12
    _check_pattern_match  CC=2  out:3
    _collect_file_contents  CC=4  out:3
    _detect_stack  CC=4  out:4
    _get_connector  CC=1  out:1
    _get_extension  CC=1  out:1
    _get_subtree_lines  CC=4  out:3
    _get_tree_symbol  CC=4  out:0
    _parse_cargo  CC=3  out:4
    _parse_package_json  CC=2  out:4
  src.lane.providers.openai_compat  [8 funcs]
    __init__  CC=5  out:2
    _call_api  CC=5  out:12
    generate_plan  CC=1  out:2
    _create_task_from_dict  CC=6  out:20
    _parse_json_response  CC=3  out:5
    _parse_response  CC=1  out:8
    _parse_tasks_from_data  CC=2  out:4
    _strip_markdown_fences  CC=3  out:4
  src.lane.ticket_generator  [12 funcs]
    _build_todo_section  CC=4  out:5
    _ensure_planfile_installed  CC=3  out:5
    _map_priority  CC=1  out:2
    _remove_generated_todo_sections  CC=1  out:5
    _remove_legacy_generated_todo_sections  CC=6  out:4
    _remove_managed_todo_blocks  CC=5  out:3
    _resolve_todo_path  CC=3  out:1
    _sync_todo_section  CC=2  out:6
    export_to_planfile_yaml  CC=3  out:4
    sync_to_planfile  CC=8  out:12

EDGES:
  src.lane.cli.cmd_plan → src.lane.config.get_settings
  src.lane.cli.cmd_print_context → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_context → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.project_analyzer.analyze_project
  src.lane.cli.cmd_print_prompt → src.lane.git_reader.read_git_context
  src.lane.cli.cmd_print_prompt → src.lane.llm_client.build_user_prompt
  src.lane.cli._sync_todos_if_requested → src.lane.ticket_generator.sync_to_todo_md
  src.lane.cli._sync_planfile_if_requested → src.lane.ticket_generator.sync_to_planfile
  src.lane.cli._export_yaml_if_requested → src.lane.ticket_generator.export_to_planfile_yaml
  src.lane.cli._display_tickets → src.lane.cli._get_priority_emoji
  src.lane.cli.cmd_metrics → src.lane.metrics.complexity.collect_file_metrics
  src.lane.cli.cmd_auto → src.lane.metrics.hotspots.identify_bug_hotspots
  src.lane.cli.cmd_auto → src.lane.metrics.complexity.collect_file_metrics
  src.lane.git_reader._is_git_repo → src.lane.git_reader._run
  src.lane.git_reader._run_git_command → src.lane.git_reader._run
  src.lane.git_reader._get_git_branch → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_remote → src.lane.git_reader._run_git_command
  src.lane.git_reader._get_git_commits → src.lane.git_reader._run
  src.lane.git_reader._get_git_commits → src.lane.git_reader._parse_commits
  src.lane.git_reader._count_file_frequencies → src.lane.git_reader._should_ignore_git_path
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._run
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._count_file_frequencies
  src.lane.git_reader._get_file_frequency → src.lane.git_reader._format_file_summary
  src.lane.git_reader._get_git_todos → src.lane.git_reader._run
  src.lane.git_reader._get_git_todos → src.lane.git_reader._should_include_todo_line
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_branch
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_remote
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_commits
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_file_frequency
  src.lane.git_reader.read_git_context → src.lane.git_reader._get_git_todos
  src.lane.git_reader.read_git_context → src.lane.git_reader._is_git_repo
  src.lane.git_reader.read_git_context → src.lane.git_reader._create_empty_context
  src.lane.git_reader._create_commit_info → src.lane.git_reader._filter_git_paths
  src.lane.git_reader._finalize_commit → src.lane.git_reader._create_commit_info
  src.lane.git_reader._parse_commits → src.lane.git_reader._finalize_commit
  src.lane.git_reader._parse_commits → src.lane.git_reader._parse_commit_metadata
  src.lane.git_reader._filter_git_paths → src.lane.git_reader._should_ignore_git_path
  src.lane.git_reader._should_include_todo_line → src.lane.git_reader._should_ignore_git_path
  src.lane.planner.generate_next_tasks → src.lane.project_analyzer.analyze_project
  src.lane.planner.generate_next_tasks → src.lane.git_reader.read_git_context
  src.lane.planner.generate_next_tasks → src.lane.llm_client.build_user_prompt
  src.lane.planner.generate_next_tasks → src.lane.config.get_settings
  src.lane.planner.generate_next_tasks → src.lane.koru_context.build_koru_context
  src.lane.llm_client.parse_task_plan_response → src.lane.providers.openai_compat._parse_response
  src.lane.llm_client.OpenAICompatibleLLMClient.generate_task_plan → src.lane.llm_client.build_user_prompt
  src.lane.koru_context.build_koru_context → src.lane.koru_context._load_operations
  src.lane.koru_context.build_koru_context → src.lane.koru_context._format_operations_for_llm
  src.lane.koru_context.build_koru_context → src.lane.koru_context._format_project_state_for_llm
  src.lane.koru_context.build_koru_context → src.lane.koru_context._load_project_state
  src.lane.ticket_generator.task_plan_to_tickets → src.lane.ticket_generator._map_priority
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 26f 3770L | python:19,yaml:4,txt:1,shell:1,toml:1 | 2026-05-29
# generated in 0.01s
# CC̅=4.0 | critical:2/111 | dups:0 | cycles:1

HEALTH[3]:
  🔴 CYCLE Circular dependency detected: src.lane.project_analyzer._get_subtree_lines -> src.lane.project_analyzer._build_tree. This indicates high coupling and may lead to infinite recursion or initialization issues.
  🟡 CC    identify_bug_hotspots CC=16 (limit:15)
  🟡 CC    collect_coupling_matrix CC=18 (limit:15)

REFACTOR[2]:
  1. split 2 high-CC methods  (CC>15)
  2. break 1 circular dependencies

PIPELINES[23]:
  [1] Src [__str__]: __str__
      PURITY: 100% pure
  [2] Src [to_dict]: to_dict
      PURITY: 100% pure
  [3] Src [__str__]: __str__
      PURITY: 100% pure
  [4] Src [to_dict]: to_dict
      PURITY: 100% pure
  [5] Src [cmd_plan]: cmd_plan → get_settings
      PURITY: 100% pure
  [6] Src [cmd_print_context]: cmd_print_context → analyze_project → _collect_file_contents → _read_file_safely
      PURITY: 100% pure
  [7] Src [cmd_print_prompt]: cmd_print_prompt → analyze_project → _collect_file_contents → _read_file_safely
      PURITY: 100% pure
  [8] Src [cmd_validate]: cmd_validate
      PURITY: 100% pure
  [9] Src [cmd_tickets]: cmd_tickets → get_settings
      PURITY: 100% pure
  [10] Src [cmd_metrics]: cmd_metrics → collect_file_metrics → _calculate_fan_in
      PURITY: 100% pure
  [11] Src [cmd_auto]: cmd_auto → identify_bug_hotspots → _get_file_commits_with_info
      PURITY: 100% pure
  [12] Src [app_entry]: app_entry
      PURITY: 100% pure
  [13] Src [main]: main → get_settings
      PURITY: 100% pure
  [14] Src [__str__]: __str__
      PURITY: 100% pure
  [15] Src [to_text]: to_text
      PURITY: 100% pure
  [16] Src [parse_task_plan_response]: parse_task_plan_response → _parse_response → _strip_markdown_fences
      PURITY: 100% pure
  [17] Src [__init__]: __init__
      PURITY: 100% pure
  [18] Src [generate_task_plan]: generate_task_plan → build_user_prompt
      PURITY: 100% pure
  [19] Src [to_text]: to_text
      PURITY: 100% pure
  [20] Src [__init__]: __init__ → get_settings
      PURITY: 100% pure
  [21] Src [generate_plan]: generate_plan → _parse_response → _strip_markdown_fences
      PURITY: 100% pure
  [22] Src [_call_api]: _call_api → get_koru_system_prompt_extension
      PURITY: 100% pure
  [23] Src [get_critical_bus_factor_files]: get_critical_bus_factor_files → calculate_bus_factor
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.0    ←in:0  →out:0
  │ cli                        380L  0C   14m  CC=11     ←0
  │ complexity                 300L  1C    8m  CC=14     ←1
  │ koru_context               283L  3C    6m  CC=7      ←2
  │ project_analyzer           282L  1C   20m  CC=6      ←2
  │ ticket_generator           280L  0C   12m  CC=8      ←1
  │ !! hotspots                   270L  1C    5m  CC=16     ←1
  │ git_reader                 268L  2C   21m  CC=7      ←2
  │ openai_compat              204L  1C    8m  CC=6      ←1
  │ !! coupling                   194L  1C    3m  CC=18     ←1
  │ models                      90L  4C    4m  CC=7      ←0
  │ llm_client                  85L  1C    4m  CC=3      ←2
  │ output                      67L  0C    3m  CC=4      ←1
  │ planner                     58L  0C    1m  CC=5      ←1
  │ config                      44L  1C    1m  CC=2      ←3
  │ __init__                    31L  0C    0m  CC=0.0    ←0
  │ base                        19L  1C    1m  CC=1      ←0
  │ __init__                    16L  0C    0m  CC=0.0    ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ strategy.yaml              142L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              98L  0C    0m  CC=0.0    ←0
  │ tree.txt                    57L  0C    0m  CC=0.0    ←0
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
# redup/duplication | 2 groups | 19f 2883L | 2026-05-29

SUMMARY:
  files_scanned: 19
  total_lines:   2883
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   6
  scan_ms:       2346

HOTSPOTS[2] (files with most duplication):
  src/lane/git_reader.py  dup=6L  groups=1  frags=2  (0.2%)
  src/lane/project_analyzer.py  dup=6L  groups=1  frags=2  (0.2%)

DUPLICATES[2] (ranked by impact):
  [398e7fc98c20a6ea]   STRU  _get_git_branch  L=3 N=2 saved=3 sim=1.00
      src/lane/git_reader.py:109-111  (_get_git_branch)
      src/lane/git_reader.py:114-116  (_get_git_remote)
  [dba932c7fb158cc5]   STRU  _get_connector  L=3 N=2 saved=3 sim=1.00
      src/lane/project_analyzer.py:245-247  (_get_connector)
      src/lane/project_analyzer.py:250-252  (_get_extension)

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
# code2llm/evolution | 111 func | 15f | 2026-05-29
# generated in 0.00s

NEXT[3] (ranked by impact):
  [1] !  SPLIT-FUNC      identify_bug_hotspots  CC=16  fan=16
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 256

  [2] !  SPLIT-FUNC      collect_coupling_matrix  CC=18  fan=11
      WHY: CC=18 exceeds 15
      EFFORT: ~1h  IMPACT: 198

  [3] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          4.0 → ≤2.8
  max-CC:      18 → ≤9
  god-modules: 1 → 0
  high-CC(≥15): 2 → ≤1
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
  prev CC̄=2.7 → now CC̄=4.0
```

## Intent

Generate the next 10 project tasks from project state, git history and an LLM prompt.
