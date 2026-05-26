# lane

Generate the next 10 project tasks from project state, git history and an LLM prompt.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `lane`
- **version**: `0.2.7`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(2), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

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

## Interfaces

### CLI Entry Points

- `lane`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m lane
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m lane --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m lane --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m lane --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# NOTE: Python pytest files were detected but no convertible HTTP calls or assertions were found.
# To run pytest tests directly, use: pytest <test_file>
```

## Configuration

```yaml
project:
  name: lane
  version: 0.2.7
  env: local
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

## Deployment

```bash markpact:run
pip install lane

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`lane`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/cryptography/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# lane | 27f 2725L | python:24,shell:2,less:1 | 2026-05-26
# stats: 57 func | 22 cls | 27 mod | CC̄=2.6 | critical:0 | cycles:0
# alerts[5]: CC cmd_tickets=9; CC _build_tree=8; CC _parse_commits=7; CC cmd_plan=4; CC main=4
# hotspots[5]: cmd_tickets fan=15; main fan=15; _build_tree fan=13; cmd_plan fan=12; cmd_print_context fan=10
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[27]:
  app.doql.less,48
  project.sh,48
  src/lane/__init__.py,32
  src/lane/__main__.py,7
  src/lane/cli.py,217
  src/lane/config.py,43
  src/lane/git_reader.py,208
  src/lane/llm_client.py,78
  src/lane/models.py,91
  src/lane/output.py,68
  src/lane/planner.py,43
  src/lane/project_analyzer.py,259
  src/lane/providers/__init__.py,7
  src/lane/providers/base.py,20
  src/lane/providers/openai_compat.py,173
  src/lane/ticket_generator.py,166
  tests/test_cli.py,201
  tests/test_config.py,52
  tests/test_git_reader.py,162
  tests/test_llm_client.py,105
  tests/test_models.py,88
  tests/test_output.py,70
  tests/test_planner.py,93
  tests/test_project_analyzer.py,182
  tests/test_providers.py,134
  tests/test_ticket_generator.py,128
  tree.sh,2
D:
  src/lane/__init__.py:
  src/lane/__main__.py:
  src/lane/cli.py:
    e: cmd_plan,cmd_print_context,cmd_print_prompt,cmd_validate,cmd_tickets,app_entry,main
    cmd_plan(repo;extra_context;model;base_url;as_json;max_commits)
    cmd_print_context(repo;max_commits;raw)
    cmd_print_prompt(repo;extra_context;max_commits)
    cmd_validate(plan_file)
    cmd_tickets(repo;extra_context;model;base_url;max_commits;sync_todo;export_yaml;output_path)
    app_entry()
    main(argv)
  src/lane/config.py:
    e: get_settings,LaneSettings
    LaneSettings: api_key(0)  # Runtime configuration loaded from environment variables.
    get_settings()
  src/lane/git_reader.py:
    e: _run,_is_git_repo,_run_git_command,_get_git_branch,_get_git_remote,_get_git_commits,_count_file_frequencies,_format_file_summary,_get_file_frequency,_get_git_todos,_create_empty_context,read_git_context,_parse_commit_metadata,_create_commit_info,_parse_commits,CommitInfo,GitContext
    CommitInfo: __str__(0)
    GitContext: to_text(0)
    _run(cmd;cwd)
    _is_git_repo(path)
    _run_git_command(repo_path;command;default)
    _get_git_branch(repo_path)
    _get_git_remote(repo_path)
    _get_git_commits(repo_path;max_commits)
    _count_file_frequencies(raw_output)
    _format_file_summary(file_freq)
    _get_file_frequency(repo_path;max_commits)
    _get_git_todos(repo_path)
    _create_empty_context(repo_path)
    read_git_context(repo_path;max_commits)
    _parse_commit_metadata(line)
    _create_commit_info(meta;files)
    _parse_commits(log_raw)
  src/lane/llm_client.py:
    e: build_user_prompt,parse_task_plan_response,OpenAICompatibleLLMClient
    OpenAICompatibleLLMClient: __init__(4),generate_task_plan(4)  # Minimal client for OpenRouter or another OpenAI-compatible e
    build_user_prompt(project_snapshot_text;git_context_text;extra_context)
    parse_task_plan_response(raw;project_name;model)
  src/lane/models.py:
    e: Priority,TaskType,Task,TaskPlan
    Priority:
    TaskType:
    Task: __str__(0),to_dict(0)
    TaskPlan: __str__(0),to_dict(0)
  src/lane/output.py:
    e: render_plan,render_plan_json,render_context
    render_plan(plan;console)
    render_plan_json(plan;console)
    render_context(project_text;git_text;console)
  src/lane/planner.py:
    e: generate_next_tasks
    generate_next_tasks(repo_path;extra_context;provider;settings)
  src/lane/project_analyzer.py:
    e: _read_file_safely,_truncate_file_content,_collect_file_contents,_resolve_name_and_description,analyze_project,_check_pattern_match,_detect_stack,_parse_pyproject_tomllib,_parse_pyproject_regex,_parse_pyproject,_parse_package_json,_parse_cargo,_readme_summary,_should_ignore_entry,_get_tree_symbol,_get_connector,_get_extension,_build_tree,ProjectSnapshot
    ProjectSnapshot: to_text(0)
    _read_file_safely(path)
    _truncate_file_content(text)
    _collect_file_contents(root)
    _resolve_name_and_description(root;file_contents;default_name)
    analyze_project(root)
    _check_pattern_match(root;pattern)
    _detect_stack(root)
    _parse_pyproject_tomllib(text;fallback)
    _parse_pyproject_regex(text;fallback)
    _parse_pyproject(text;fallback)
    _parse_package_json(path;fallback)
    _parse_cargo(text;fallback)
    _readme_summary(text)
    _should_ignore_entry(name)
    _get_tree_symbol(is_last;connector)
    _get_connector(is_last)
    _get_extension(is_last)
    _build_tree(root;max_depth;depth;prefix)
  src/lane/providers/__init__.py:
  src/lane/providers/base.py:
    e: LLMProvider
    LLMProvider: generate_plan(2)  # Interface every LLM backend must implement.
  src/lane/providers/openai_compat.py:
    e: _strip_markdown_fences,_parse_json_response,_create_task_from_dict,_parse_tasks_from_data,_parse_response,OpenAICompatProvider
    OpenAICompatProvider: __init__(5),generate_plan(2),_call_api(1)  # Provider for OpenRouter or any OpenAI-compatible endpoint.
    _strip_markdown_fences(raw)
    _parse_json_response(raw)
    _create_task_from_dict(item;task_index)
    _parse_tasks_from_data(data)
    _parse_response(raw;project_name;model)
  src/lane/ticket_generator.py:
    e: task_plan_to_tickets,_map_priority,sync_to_todo_md,_create_temp_strategy,export_to_planfile_yaml
    task_plan_to_tickets(task_plan)
    _map_priority(priority)
    sync_to_todo_md(task_plan;project_path)
    _create_temp_strategy(task_plan;strategy_path)
    export_to_planfile_yaml(task_plan;output_path)
  tests/test_cli.py:
    e: CLITests
    CLITests: test_print_prompt_mode_outputs_prompt(0),test_print_prompt_includes_extra_context(0),test_missing_api_key_returns_exit_1(0),test_print_context_raw_mode(0),test_json_mode_outputs_json(0),test_max_commits_override(0),test_app_entry_exists(0),test_typer_print_context_command(0),test_typer_print_prompt_command(0),test_typer_validate_command(0),test_typer_plan_command_with_mocked_provider(1),test_typer_plan_command_json_output(1),test_typer_validate_invalid_json(0),test_main_module_can_be_imported(0),test_cmd_plan_handles_value_error(1),test_app_entry_calls_app(1),test_main_json_output(1)
  tests/test_config.py:
    e: ConfigTests
    ConfigTests: test_settings_reads_openrouter_key(0),test_settings_prefers_openrouter_over_openai(0),test_settings_falls_back_to_openai_key(0),test_settings_api_key_none_when_no_key_set(0),test_settings_defaults(0)
  tests/test_git_reader.py:
    e: GitReaderTests
    GitReaderTests: test_parse_commits_keeps_files_with_each_commit(0),test_parse_commits_empty_log(0),test_parse_commits_single_commit_no_files(0),test_read_git_context_non_git_dir(0),test_git_context_to_text_no_commits(0),test_git_context_to_text_with_commits_and_files(0),test_git_context_to_text_with_todos(0),test_commit_info_str_with_many_files(0),test_run_returns_empty_on_failure(1),test_run_returns_empty_on_timeout(1),test_read_git_context_with_real_git_repo(2),test_read_git_context_with_empty_git_log(2)
  tests/test_llm_client.py:
    e: LLMClientTests
    LLMClientTests: test_build_user_prompt_includes_sections(0),test_build_user_prompt_default_extra_context(0),test_parse_task_plan_response_strips_fences(0),test_parse_task_plan_response_invalid_json_raises(0),test_parse_task_plan_response_non_object_raises(0),test_parse_task_plan_response_falls_back_to_project_name(0),test_parse_task_plan_response_invalid_priority_raises(0),test_openai_llm_client_initialization(1),test_openai_llm_client_generate_task_plan(1)
  tests/test_models.py:
    e: TaskModelTests
    TaskModelTests: test_task_string_contains_metadata(0),test_task_string_fractional_hours(0),test_task_string_no_hours(0),test_task_plan_to_dict_serializes_enums(0),test_task_plan_str_contains_header(0),test_task_plan_str_shows_dependencies(0),test_task_plan_str_includes_generated_at_when_set(0),test_task_pydantic_validation_rejects_bad_priority(0)
  tests/test_output.py:
    e: OutputTests
    OutputTests: test_render_plan_displays_summary_and_tasks(0),test_render_plan_json_outputs_valid_json(0),test_render_context_displays_both_panels(0)
  tests/test_planner.py:
    e: PlannerTests
    PlannerTests: test_generate_next_tasks_calls_provider(3),test_generate_next_tasks_uses_default_provider_when_none(3)
  tests/test_project_analyzer.py:
    e: ProjectAnalyzerTests
    ProjectAnalyzerTests: test_analyze_project_reads_pyproject_and_readme(0),test_analyze_project_no_manifest(0),test_parse_pyproject_invalid_toml_falls_back_to_regex(0),test_parse_pyproject_valid_toml(0),test_readme_summary_skips_headers(0),test_readme_summary_empty(0),test_analyze_project_readme_only(0),test_parse_package_json(0),test_parse_package_json_invalid(0),test_parse_cargo_toml(0),test_detect_stack_python(0),test_detect_stack_javascript(0),test_detect_stack_rust(0),test_detect_stack_by_extension(0),test_analyze_project_handles_oserror_on_file_read(0),test_analyze_project_truncates_large_files(0),test_analyze_project_uses_package_json_parser(0),test_analyze_project_uses_cargo_parser(0)
  tests/test_providers.py:
    e: ParseResponseTests,OpenAICompatProviderTests
    ParseResponseTests: test_valid_response_parsed(0),test_invalid_json_raises(0),test_non_object_raises(0),test_bad_task_priority_raises(0),test_fenced_code_block_stripped(0)
    OpenAICompatProviderTests: test_no_api_key_raises_value_error(0),test_generate_plan_uses_parse_response(0),test_call_api_constructs_correct_payload(1),test_call_api_sets_correct_headers(1),test_call_api_handles_unexpected_response(1)
  tests/test_ticket_generator.py:
    e: TicketGeneratorTests
    TicketGeneratorTests: test_task_plan_to_tickets(0),test_map_priority(0),test_export_to_planfile_yaml(0),test_sync_to_todo_md_without_planfile(0)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('lane', '0.2.7', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 48, 'less').
project_file('project.sh', 48, 'shell').
project_file('src/lane/__init__.py', 32, 'python').
project_file('src/lane/__main__.py', 7, 'python').
project_file('src/lane/cli.py', 217, 'python').
project_file('src/lane/config.py', 43, 'python').
project_file('src/lane/git_reader.py', 208, 'python').
project_file('src/lane/llm_client.py', 78, 'python').
project_file('src/lane/models.py', 91, 'python').
project_file('src/lane/output.py', 68, 'python').
project_file('src/lane/planner.py', 43, 'python').
project_file('src/lane/project_analyzer.py', 259, 'python').
project_file('src/lane/providers/__init__.py', 7, 'python').
project_file('src/lane/providers/base.py', 20, 'python').
project_file('src/lane/providers/openai_compat.py', 173, 'python').
project_file('src/lane/ticket_generator.py', 166, 'python').
project_file('tests/test_cli.py', 201, 'python').
project_file('tests/test_config.py', 52, 'python').
project_file('tests/test_git_reader.py', 162, 'python').
project_file('tests/test_llm_client.py', 105, 'python').
project_file('tests/test_models.py', 88, 'python').
project_file('tests/test_output.py', 70, 'python').
project_file('tests/test_planner.py', 93, 'python').
project_file('tests/test_project_analyzer.py', 182, 'python').
project_file('tests/test_providers.py', 134, 'python').
project_file('tests/test_ticket_generator.py', 128, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('src/lane/cli.py', 'cmd_plan', 6, 4, 12).
python_function('src/lane/cli.py', 'cmd_print_context', 3, 2, 10).
python_function('src/lane/cli.py', 'cmd_print_prompt', 3, 1, 10).
python_function('src/lane/cli.py', 'cmd_validate', 1, 2, 8).
python_function('src/lane/cli.py', 'cmd_tickets', 8, 9, 15).
python_function('src/lane/cli.py', 'app_entry', 0, 1, 1).
python_function('src/lane/cli.py', 'main', 1, 4, 15).
python_function('src/lane/config.py', 'get_settings', 0, 2, 1).
python_function('src/lane/git_reader.py', '_run', 2, 3, 2).
python_function('src/lane/git_reader.py', '_is_git_repo', 1, 1, 2).
python_function('src/lane/git_reader.py', '_run_git_command', 3, 2, 1).
python_function('src/lane/git_reader.py', '_get_git_branch', 1, 1, 1).
python_function('src/lane/git_reader.py', '_get_git_remote', 1, 1, 1).
python_function('src/lane/git_reader.py', '_get_git_commits', 2, 1, 2).
python_function('src/lane/git_reader.py', '_count_file_frequencies', 1, 3, 3).
python_function('src/lane/git_reader.py', '_format_file_summary', 1, 2, 2).
python_function('src/lane/git_reader.py', '_get_file_frequency', 2, 1, 3).
python_function('src/lane/git_reader.py', '_get_git_todos', 1, 3, 3).
python_function('src/lane/git_reader.py', '_create_empty_context', 1, 1, 1).
python_function('src/lane/git_reader.py', 'read_git_context', 2, 2, 8).
python_function('src/lane/git_reader.py', '_parse_commit_metadata', 1, 3, 2).
python_function('src/lane/git_reader.py', '_create_commit_info', 2, 1, 1).
python_function('src/lane/git_reader.py', '_parse_commits', 1, 7, 5).
python_function('src/lane/llm_client.py', 'build_user_prompt', 3, 2, 1).
python_function('src/lane/llm_client.py', 'parse_task_plan_response', 3, 1, 1).
python_function('src/lane/output.py', 'render_plan', 2, 4, 8).
python_function('src/lane/output.py', 'render_plan_json', 2, 2, 4).
python_function('src/lane/output.py', 'render_context', 3, 2, 3).
python_function('src/lane/planner.py', 'generate_next_tasks', 4, 3, 7).
python_function('src/lane/project_analyzer.py', '_read_file_safely', 1, 2, 1).
python_function('src/lane/project_analyzer.py', '_truncate_file_content', 1, 2, 1).
python_function('src/lane/project_analyzer.py', '_collect_file_contents', 1, 4, 3).
python_function('src/lane/project_analyzer.py', '_resolve_name_and_description', 3, 3, 5).
python_function('src/lane/project_analyzer.py', 'analyze_project', 1, 1, 5).
python_function('src/lane/project_analyzer.py', '_check_pattern_match', 2, 2, 3).
python_function('src/lane/project_analyzer.py', '_detect_stack', 1, 4, 4).
python_function('src/lane/project_analyzer.py', '_parse_pyproject_tomllib', 2, 4, 3).
python_function('src/lane/project_analyzer.py', '_parse_pyproject_regex', 2, 3, 2).
python_function('src/lane/project_analyzer.py', '_parse_pyproject', 2, 2, 2).
python_function('src/lane/project_analyzer.py', '_parse_package_json', 2, 2, 3).
python_function('src/lane/project_analyzer.py', '_parse_cargo', 2, 3, 2).
python_function('src/lane/project_analyzer.py', '_readme_summary', 1, 4, 3).
python_function('src/lane/project_analyzer.py', '_should_ignore_entry', 1, 2, 1).
python_function('src/lane/project_analyzer.py', '_get_tree_symbol', 2, 4, 0).
python_function('src/lane/project_analyzer.py', '_get_connector', 1, 1, 1).
python_function('src/lane/project_analyzer.py', '_get_extension', 1, 1, 1).
python_function('src/lane/project_analyzer.py', '_build_tree', 4, 8, 13).
python_function('src/lane/providers/openai_compat.py', '_strip_markdown_fences', 1, 3, 4).
python_function('src/lane/providers/openai_compat.py', '_parse_json_response', 1, 3, 4).
python_function('src/lane/providers/openai_compat.py', '_create_task_from_dict', 2, 2, 7).
python_function('src/lane/providers/openai_compat.py', '_parse_tasks_from_data', 1, 2, 4).
python_function('src/lane/providers/openai_compat.py', '_parse_response', 3, 1, 7).
python_function('src/lane/ticket_generator.py', 'task_plan_to_tickets', 1, 3, 2).
python_function('src/lane/ticket_generator.py', '_map_priority', 1, 1, 2).
python_function('src/lane/ticket_generator.py', 'sync_to_todo_md', 2, 3, 6).
python_function('src/lane/ticket_generator.py', '_create_temp_strategy', 2, 2, 3).
python_function('src/lane/ticket_generator.py', 'export_to_planfile_yaml', 2, 3, 4).

% ── Python Classes ───────────────────────────────────────
python_class('src/lane/config.py', 'LaneSettings').
python_method('LaneSettings', 'api_key', 0, 2, 0).
python_class('src/lane/git_reader.py', 'CommitInfo').
python_method('CommitInfo', '__str__', 0, 2, 2).
python_class('src/lane/git_reader.py', 'GitContext').
python_method('GitContext', 'to_text', 0, 7, 3).
python_class('src/lane/llm_client.py', 'OpenAICompatibleLLMClient').
python_method('OpenAICompatibleLLMClient', '__init__', 4, 3, 2).
python_method('OpenAICompatibleLLMClient', 'generate_task_plan', 4, 1, 2).
python_class('src/lane/models.py', 'Priority').
python_class('src/lane/models.py', 'TaskType').
python_class('src/lane/models.py', 'Task').
python_method('Task', '__str__', 0, 7, 2).
python_method('Task', 'to_dict', 0, 2, 1).
python_class('src/lane/models.py', 'TaskPlan').
python_method('TaskPlan', '__str__', 0, 7, 3).
python_method('TaskPlan', 'to_dict', 0, 2, 1).
python_class('src/lane/project_analyzer.py', 'ProjectSnapshot').
python_method('ProjectSnapshot', 'to_text', 0, 5, 2).
python_class('src/lane/providers/base.py', 'LLMProvider').
python_method('LLMProvider', 'generate_plan', 2, 1, 0).
python_class('src/lane/providers/openai_compat.py', 'OpenAICompatProvider').
python_method('OpenAICompatProvider', '__init__', 5, 5, 2).
python_method('OpenAICompatProvider', 'generate_plan', 2, 1, 2).
python_method('OpenAICompatProvider', '_call_api', 1, 3, 10).
python_class('tests/test_cli.py', 'CLITests').
python_method('CLITests', 'test_print_prompt_mode_outputs_prompt', 0, 1, 9).
python_method('CLITests', 'test_print_prompt_includes_extra_context', 0, 1, 8).
python_method('CLITests', 'test_missing_api_key_returns_exit_1', 0, 3, 7).
python_method('CLITests', 'test_print_context_raw_mode', 0, 1, 8).
python_method('CLITests', 'test_json_mode_outputs_json', 0, 3, 8).
python_method('CLITests', 'test_max_commits_override', 0, 1, 7).
python_method('CLITests', 'test_app_entry_exists', 0, 1, 2).
python_method('CLITests', 'test_typer_print_context_command', 0, 1, 7).
python_method('CLITests', 'test_typer_print_prompt_command', 0, 1, 7).
python_method('CLITests', 'test_typer_validate_command', 0, 1, 7).
python_method('CLITests', 'test_typer_plan_command_with_mocked_provider', 1, 1, 10).
python_method('CLITests', 'test_typer_plan_command_json_output', 1, 1, 9).
python_method('CLITests', 'test_typer_validate_invalid_json', 0, 2, 8).
python_method('CLITests', 'test_main_module_can_be_imported', 0, 1, 1).
python_method('CLITests', 'test_cmd_plan_handles_value_error', 1, 1, 9).
python_method('CLITests', 'test_app_entry_calls_app', 1, 1, 3).
python_method('CLITests', 'test_main_json_output', 1, 1, 8).
python_class('tests/test_config.py', 'ConfigTests').
python_method('ConfigTests', 'test_settings_reads_openrouter_key', 0, 1, 3).
python_method('ConfigTests', 'test_settings_prefers_openrouter_over_openai', 0, 1, 3).
python_method('ConfigTests', 'test_settings_falls_back_to_openai_key', 0, 3, 4).
python_method('ConfigTests', 'test_settings_api_key_none_when_no_key_set', 0, 3, 4).
python_method('ConfigTests', 'test_settings_defaults', 0, 1, 2).
python_class('tests/test_git_reader.py', 'GitReaderTests').
python_method('GitReaderTests', 'test_parse_commits_keeps_files_with_each_commit', 0, 1, 4).
python_method('GitReaderTests', 'test_parse_commits_empty_log', 0, 1, 2).
python_method('GitReaderTests', 'test_parse_commits_single_commit_no_files', 0, 1, 3).
python_method('GitReaderTests', 'test_read_git_context_non_git_dir', 0, 1, 4).
python_method('GitReaderTests', 'test_git_context_to_text_no_commits', 0, 1, 4).
python_method('GitReaderTests', 'test_git_context_to_text_with_commits_and_files', 0, 1, 5).
python_method('GitReaderTests', 'test_git_context_to_text_with_todos', 0, 1, 4).
python_method('GitReaderTests', 'test_commit_info_str_with_many_files', 0, 2, 4).
python_method('GitReaderTests', 'test_run_returns_empty_on_failure', 1, 1, 5).
python_method('GitReaderTests', 'test_run_returns_empty_on_timeout', 1, 1, 5).
python_method('GitReaderTests', 'test_read_git_context_with_real_git_repo', 2, 1, 5).
python_method('GitReaderTests', 'test_read_git_context_with_empty_git_log', 2, 1, 5).
python_class('tests/test_llm_client.py', 'LLMClientTests').
python_method('LLMClientTests', 'test_build_user_prompt_includes_sections', 0, 1, 2).
python_method('LLMClientTests', 'test_build_user_prompt_default_extra_context', 0, 1, 2).
python_method('LLMClientTests', 'test_parse_task_plan_response_strips_fences', 0, 1, 2).
python_method('LLMClientTests', 'test_parse_task_plan_response_invalid_json_raises', 0, 1, 4).
python_method('LLMClientTests', 'test_parse_task_plan_response_non_object_raises', 0, 1, 5).
python_method('LLMClientTests', 'test_parse_task_plan_response_falls_back_to_project_name', 0, 1, 3).
python_method('LLMClientTests', 'test_parse_task_plan_response_invalid_priority_raises', 0, 1, 3).
python_method('LLMClientTests', 'test_openai_llm_client_initialization', 1, 1, 4).
python_method('LLMClientTests', 'test_openai_llm_client_generate_task_plan', 1, 1, 7).
python_class('tests/test_models.py', 'TaskModelTests').
python_method('TaskModelTests', 'test_task_string_contains_metadata', 0, 1, 3).
python_method('TaskModelTests', 'test_task_string_fractional_hours', 0, 1, 3).
python_method('TaskModelTests', 'test_task_string_no_hours', 0, 1, 3).
python_method('TaskModelTests', 'test_task_plan_to_dict_serializes_enums', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_contains_header', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_shows_dependencies', 0, 1, 4).
python_method('TaskModelTests', 'test_task_plan_str_includes_generated_at_when_set', 0, 1, 3).
python_method('TaskModelTests', 'test_task_pydantic_validation_rejects_bad_priority', 0, 1, 2).
python_class('tests/test_output.py', 'OutputTests').
python_method('OutputTests', 'test_render_plan_displays_summary_and_tasks', 0, 1, 7).
python_method('OutputTests', 'test_render_plan_json_outputs_valid_json', 0, 1, 7).
python_method('OutputTests', 'test_render_context_displays_both_panels', 0, 1, 5).
python_class('tests/test_planner.py', 'PlannerTests').
python_method('PlannerTests', 'test_generate_next_tasks_calls_provider', 3, 1, 8).
python_method('PlannerTests', 'test_generate_next_tasks_uses_default_provider_when_none', 3, 1, 8).
python_class('tests/test_project_analyzer.py', 'ProjectAnalyzerTests').
python_method('ProjectAnalyzerTests', 'test_analyze_project_reads_pyproject_and_readme', 0, 1, 8).
python_method('ProjectAnalyzerTests', 'test_analyze_project_no_manifest', 0, 1, 4).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_invalid_toml_falls_back_to_regex', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_parse_pyproject_valid_toml', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_readme_summary_skips_headers', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_readme_summary_empty', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_analyze_project_readme_only', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_package_json', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_package_json_invalid', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_parse_cargo_toml', 0, 1, 2).
python_method('ProjectAnalyzerTests', 'test_detect_stack_python', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_javascript', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_rust', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_detect_stack_by_extension', 0, 1, 6).
python_method('ProjectAnalyzerTests', 'test_analyze_project_handles_oserror_on_file_read', 0, 2, 6).
python_method('ProjectAnalyzerTests', 'test_analyze_project_truncates_large_files', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_analyze_project_uses_package_json_parser', 0, 1, 5).
python_method('ProjectAnalyzerTests', 'test_analyze_project_uses_cargo_parser', 0, 1, 5).
python_class('tests/test_providers.py', 'ParseResponseTests').
python_method('ParseResponseTests', 'test_valid_response_parsed', 0, 1, 3).
python_method('ParseResponseTests', 'test_invalid_json_raises', 0, 1, 4).
python_method('ParseResponseTests', 'test_non_object_raises', 0, 1, 5).
python_method('ParseResponseTests', 'test_bad_task_priority_raises', 0, 1, 5).
python_method('ParseResponseTests', 'test_fenced_code_block_stripped', 0, 1, 2).
python_class('tests/test_providers.py', 'OpenAICompatProviderTests').
python_method('OpenAICompatProviderTests', 'test_no_api_key_raises_value_error', 0, 1, 6).
python_method('OpenAICompatProviderTests', 'test_generate_plan_uses_parse_response', 0, 1, 5).
python_method('OpenAICompatProviderTests', 'test_call_api_constructs_correct_payload', 1, 1, 8).
python_method('OpenAICompatProviderTests', 'test_call_api_sets_correct_headers', 1, 1, 5).
python_method('OpenAICompatProviderTests', 'test_call_api_handles_unexpected_response', 1, 1, 7).
python_class('tests/test_ticket_generator.py', 'TicketGeneratorTests').
python_method('TicketGeneratorTests', 'test_task_plan_to_tickets', 0, 1, 5).
python_method('TicketGeneratorTests', 'test_map_priority', 0, 1, 2).
python_method('TicketGeneratorTests', 'test_export_to_planfile_yaml', 0, 1, 11).
python_method('TicketGeneratorTests', 'test_sync_to_todo_md_without_planfile', 0, 1, 7).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
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

## Intent

Generate the next 10 project tasks from project state, git history and an LLM prompt.
