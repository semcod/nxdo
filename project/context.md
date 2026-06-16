# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/semcod/nxdo
- **Primary Language**: python
- **Languages**: python: 19, yaml: 4, txt: 1, shell: 1, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 111
- **Total Classes**: 17
- **Modules**: 26
- **Entry Points**: 26

## Architecture by Module

### src.nxdo.git_reader
- **Functions**: 21
- **Classes**: 2
- **File**: `git_reader.py`

### src.nxdo.project_analyzer
- **Functions**: 20
- **Classes**: 1
- **File**: `project_analyzer.py`

### src.nxdo.cli
- **Functions**: 14
- **File**: `cli.py`

### src.nxdo.ticket_generator
- **Functions**: 12
- **File**: `ticket_generator.py`

### src.nxdo.providers.openai_compat
- **Functions**: 8
- **Classes**: 1
- **File**: `openai_compat.py`

### src.nxdo.metrics.complexity
- **Functions**: 8
- **Classes**: 1
- **File**: `complexity.py`

### src.nxdo.koru_context
- **Functions**: 6
- **Classes**: 3
- **File**: `koru_context.py`

### src.nxdo.metrics.hotspots
- **Functions**: 5
- **Classes**: 1
- **File**: `hotspots.py`

### src.nxdo.llm_client
- **Functions**: 4
- **Classes**: 1
- **File**: `llm_client.py`

### src.nxdo.models
- **Functions**: 4
- **Classes**: 4
- **File**: `models.py`

### src.nxdo.output
- **Functions**: 3
- **File**: `output.py`

### src.nxdo.metrics.coupling
- **Functions**: 3
- **Classes**: 1
- **File**: `coupling.py`

### src.nxdo.config
- **Functions**: 1
- **Classes**: 1
- **File**: `config.py`

### src.nxdo.planner
- **Functions**: 1
- **File**: `planner.py`

### src.nxdo.providers.base
- **Functions**: 1
- **Classes**: 1
- **File**: `base.py`

## Key Entry Points

Main execution flows into the system:

### src.nxdo.cli.cmd_metrics
> Display code metrics: complexity, coupling, hotspots.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, repo.resolve, console.print, console.print, src.nxdo.metrics.complexity.collect_file_metrics

### src.nxdo.cli.cmd_auto
> Auto-generate and sync tickets for the most important work.

This command automatically:
1. Analyzes the project for high-priority issues (hotspots, c
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, repo.resolve, console.print, console.print, src.nxdo.metrics.hotspots.identify_bug_hotspots

### src.nxdo.cli.cmd_tickets
> Generate tickets from a plan using planfile integration.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option

### src.nxdo.cli.main
> Compatibility shim — maps legacy argparse argv to Typer sub-commands.
- **Calls**: argparse.ArgumentParser, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument, parser.add_argument

### src.nxdo.cli.cmd_plan
> Generate a 10-task plan for the repository.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, src.nxdo.config.get_settings

### src.nxdo.cli.cmd_print_context
> Print the assembled project and git context (no LLM call).
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, src.nxdo.project_analyzer.analyze_project, src.nxdo.git_reader.read_git_context, snapshot.to_text, git_ctx.to_text

### src.nxdo.cli.cmd_print_prompt
> Print the full prompt that would be sent to the LLM.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, src.nxdo.project_analyzer.analyze_project, src.nxdo.git_reader.read_git_context, src.nxdo.llm_client.build_user_prompt, print

### src.nxdo.providers.openai_compat.OpenAICompatProvider._call_api
- **Calls**: retry, ValueError, src.nxdo.koru_context.get_koru_system_prompt_extension, httpx.Client, client.post, response.json, None.strip, retry_if_exception_type

### src.nxdo.models.TaskPlan.__str__
- **Calls**: None.join, lines.append, lines.append, lines.append, lines.append, str, lines.append, None.join

### src.nxdo.metrics.hotspots.get_critical_bus_factor_files
> Get files with critical bus factor (1-2 authors) + their authors.

Returns:
    [(file_path, author_count, [author_names]), ...]
- **Calls**: bus_factors.items, critical.sort, src.nxdo.metrics.hotspots.calculate_bus_factor, subprocess.run, list, critical.append, set, line.strip

### src.nxdo.cli.cmd_validate
> Validate a saved JSON plan file against the TaskPlan schema.
- **Calls**: app.command, typer.Argument, console.print, json.loads, TaskPlan.model_validate, plan_file.read_text, err_console.print, typer.Exit

### src.nxdo.git_reader.GitContext.to_text
- **Calls**: None.join, lines.append, lines.append, lines.append, lines.append, lines.append, len

### src.nxdo.git_reader.CommitInfo.__str__
- **Calls**: None.join, len, len

### src.nxdo.llm_client.OpenAICompatibleLLMClient.__init__
- **Calls**: OpenAICompatProvider, os.environ.get, os.environ.get

### src.nxdo.project_analyzer.ProjectSnapshot.to_text
- **Calls**: self.file_contents.items, None.join, None.join

### src.nxdo.models.Task.__str__
- **Calls**: self.task_type.value.upper, int, int

### src.nxdo.llm_client.OpenAICompatibleLLMClient.generate_task_plan
- **Calls**: src.nxdo.llm_client.build_user_prompt, self._provider.generate_plan

### src.nxdo.providers.openai_compat.OpenAICompatProvider.__init__
- **Calls**: None.rstrip, src.nxdo.config.get_settings

### src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan
- **Calls**: self._call_api, src.nxdo.providers.openai_compat._parse_response

### src.nxdo.cli.app_entry
> Entry point used by the installed `nxdo` script.
- **Calls**: app

### src.nxdo.llm_client.parse_task_plan_response
> Parse a raw JSON string from the LLM into a TaskPlan. (Compatibility wrapper.)
- **Calls**: src.nxdo.providers.openai_compat._parse_response

### src.nxdo.models.Task.to_dict
- **Calls**: self.model_dump

### src.nxdo.models.TaskPlan.to_dict
- **Calls**: task.to_dict

### src.nxdo.providers.base.LLMProvider.generate_plan
> Send *user_prompt* to the model and return a validated TaskPlan.

### src.nxdo.metrics.complexity.get_high_complexity_files
> Filter files with high complexity or coupling.

### src.nxdo.metrics.complexity.get_poorly_typed_files
> Filter files with low type coverage.

## Process Flows

Key execution flows identified:

### Flow 1: cmd_metrics
```
cmd_metrics [src.nxdo.cli]
```

### Flow 2: cmd_auto
```
cmd_auto [src.nxdo.cli]
```

### Flow 3: cmd_tickets
```
cmd_tickets [src.nxdo.cli]
```

### Flow 4: main
```
main [src.nxdo.cli]
```

### Flow 5: cmd_plan
```
cmd_plan [src.nxdo.cli]
```

### Flow 6: cmd_print_context
```
cmd_print_context [src.nxdo.cli]
  └─ →> analyze_project
      └─> _collect_file_contents
          └─> _read_file_safely
          └─> _truncate_file_content
```

### Flow 7: cmd_print_prompt
```
cmd_print_prompt [src.nxdo.cli]
  └─ →> analyze_project
      └─> _collect_file_contents
          └─> _read_file_safely
          └─> _truncate_file_content
```

### Flow 8: _call_api
```
_call_api [src.nxdo.providers.openai_compat.OpenAICompatProvider]
  └─ →> get_koru_system_prompt_extension
```

### Flow 9: __str__
```
__str__ [src.nxdo.models.TaskPlan]
```

### Flow 10: get_critical_bus_factor_files
```
get_critical_bus_factor_files [src.nxdo.metrics.hotspots]
  └─> calculate_bus_factor
```

## Key Classes

### src.nxdo.providers.openai_compat.OpenAICompatProvider
> Provider for OpenRouter or any OpenAI-compatible endpoint.
- **Methods**: 3
- **Key Methods**: src.nxdo.providers.openai_compat.OpenAICompatProvider.__init__, src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan, src.nxdo.providers.openai_compat.OpenAICompatProvider._call_api
- **Inherits**: LLMProvider

### src.nxdo.llm_client.OpenAICompatibleLLMClient
> Minimal client for OpenRouter or another OpenAI-compatible endpoint.

Kept for backwards compatibili
- **Methods**: 2
- **Key Methods**: src.nxdo.llm_client.OpenAICompatibleLLMClient.__init__, src.nxdo.llm_client.OpenAICompatibleLLMClient.generate_task_plan

### src.nxdo.models.Task
- **Methods**: 2
- **Key Methods**: src.nxdo.models.Task.__str__, src.nxdo.models.Task.to_dict
- **Inherits**: BaseModel

### src.nxdo.models.TaskPlan
- **Methods**: 2
- **Key Methods**: src.nxdo.models.TaskPlan.__str__, src.nxdo.models.TaskPlan.to_dict
- **Inherits**: BaseModel

### src.nxdo.config.NxdoSettings
> Runtime configuration loaded from environment variables.
- **Methods**: 1
- **Key Methods**: src.nxdo.config.NxdoSettings.api_key
- **Inherits**: BaseSettings

### src.nxdo.git_reader.CommitInfo
- **Methods**: 1
- **Key Methods**: src.nxdo.git_reader.CommitInfo.__str__

### src.nxdo.git_reader.GitContext
- **Methods**: 1
- **Key Methods**: src.nxdo.git_reader.GitContext.to_text

### src.nxdo.project_analyzer.ProjectSnapshot
- **Methods**: 1
- **Key Methods**: src.nxdo.project_analyzer.ProjectSnapshot.to_text

### src.nxdo.providers.base.LLMProvider
> Interface every LLM backend must implement.
- **Methods**: 1
- **Key Methods**: src.nxdo.providers.base.LLMProvider.generate_plan
- **Inherits**: ABC

### src.nxdo.koru_context.KoruOperation
> A single koru operation available for task planning.
- **Methods**: 0

### src.nxdo.koru_context.KoruProjectState
> Current project state as seen by koru.
- **Methods**: 0

### src.nxdo.koru_context.KoruContext
> Full koru context for enriching the nxdo LLM prompt.
- **Methods**: 0

### src.nxdo.models.Priority
- **Methods**: 0
- **Inherits**: str, Enum

### src.nxdo.models.TaskType
- **Methods**: 0
- **Inherits**: str, Enum

### src.nxdo.metrics.complexity.FileMetrics
> Comprehensive metrics for a source file.
- **Methods**: 0

### src.nxdo.metrics.hotspots.HotspotMetrics
> Bug hotspot metrics for a file.
- **Methods**: 0

### src.nxdo.metrics.coupling.CouplingMetrics
> Metrics for file pair coupling.
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### src.nxdo.cli.cmd_validate
> Validate a saved JSON plan file against the TaskPlan schema.
- **Output to**: app.command, typer.Argument, console.print, json.loads, TaskPlan.model_validate

### src.nxdo.git_reader._format_file_summary
> Format file frequency summary as a list of strings.
- **Output to**: sorted, file_freq.items

### src.nxdo.git_reader._parse_commit_metadata
> Parse a commit metadata line and return hash, author, date, message.
- **Output to**: line.split, len

### src.nxdo.git_reader._parse_commits
> Parse git log output into list of CommitInfo objects.
- **Output to**: log_raw.splitlines, src.nxdo.git_reader._finalize_commit, src.nxdo.git_reader._parse_commit_metadata, src.nxdo.git_reader._finalize_commit, line.strip

### src.nxdo.llm_client.parse_task_plan_response
> Parse a raw JSON string from the LLM into a TaskPlan. (Compatibility wrapper.)
- **Output to**: src.nxdo.providers.openai_compat._parse_response

### src.nxdo.koru_context._format_operations_for_llm
> Format koru operations as structured text for LLM prompt.
- **Output to**: lines.append, sorted, None.join, None.append, by_domain.items

### src.nxdo.koru_context._format_project_state_for_llm
> Format current koru project state for LLM prompt.
- **Output to**: lines.append, lines.append, lines.append, lines.append, None.join

### src.nxdo.project_analyzer._parse_pyproject_tomllib
> Parse pyproject.toml using tomllib if available.
- **Output to**: parsed.get, isinstance, tomllib.loads, project.get, project.get

### src.nxdo.project_analyzer._parse_pyproject_regex
> Parse pyproject.toml using regex fallback.
- **Output to**: re.search, re.search, name_match.group, description_match.group

### src.nxdo.project_analyzer._parse_pyproject
- **Output to**: src.nxdo.project_analyzer._parse_pyproject_tomllib, src.nxdo.project_analyzer._parse_pyproject_regex

### src.nxdo.project_analyzer._parse_package_json
- **Output to**: json.loads, data.get, data.get, path.read_text

### src.nxdo.project_analyzer._parse_cargo
- **Output to**: re.search, re.search, name_match.group, description_match.group

### src.nxdo.providers.openai_compat._parse_json_response
> Parse JSON from raw response with error handling.
- **Output to**: json.loads, isinstance, ValueError, ValueError, type

### src.nxdo.providers.openai_compat._parse_tasks_from_data
> Parse tasks from the response data.
- **Output to**: enumerate, data.get, tasks.append, src.nxdo.providers.openai_compat._create_task_from_dict

### src.nxdo.providers.openai_compat._parse_response
> Parse and validate the raw JSON response from the LLM.
- **Output to**: src.nxdo.providers.openai_compat._strip_markdown_fences, src.nxdo.providers.openai_compat._parse_json_response, src.nxdo.providers.openai_compat._parse_tasks_from_data, TaskPlan, data.get

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `src.nxdo.cli.cmd_metrics` - 33 calls
- `src.nxdo.cli.cmd_auto` - 33 calls
- `src.nxdo.cli.cmd_tickets` - 28 calls
- `src.nxdo.cli.main` - 25 calls
- `src.nxdo.metrics.hotspots.identify_bug_hotspots` - 18 calls
- `src.nxdo.cli.cmd_plan` - 16 calls
- `src.nxdo.metrics.complexity.collect_file_metrics` - 16 calls
- `src.nxdo.cli.cmd_print_context` - 14 calls
- `src.nxdo.output.render_plan` - 14 calls
- `src.nxdo.metrics.hotspots.calculate_bus_factor` - 14 calls
- `src.nxdo.cli.cmd_print_prompt` - 13 calls
- `src.nxdo.metrics.coupling.collect_coupling_matrix` - 13 calls
- `src.nxdo.metrics.coupling.get_coupling_clusters` - 13 calls
- `src.nxdo.ticket_generator.sync_to_planfile` - 12 calls
- `src.nxdo.metrics.hotspots.get_critical_bus_factor_files` - 11 calls
- `src.nxdo.cli.cmd_validate` - 9 calls
- `src.nxdo.planner.generate_next_tasks` - 9 calls
- `src.nxdo.koru_context.build_koru_context` - 9 calls
- `src.nxdo.git_reader.read_git_context` - 8 calls
- `src.nxdo.git_reader.GitContext.to_text` - 7 calls
- `src.nxdo.ticket_generator.sync_to_todo_md` - 6 calls
- `src.nxdo.output.render_context` - 5 calls
- `src.nxdo.project_analyzer.analyze_project` - 5 calls
- `src.nxdo.output.render_plan_json` - 4 calls
- `src.nxdo.ticket_generator.export_to_planfile_yaml` - 4 calls
- `src.nxdo.project_analyzer.ProjectSnapshot.to_text` - 3 calls
- `src.nxdo.llm_client.OpenAICompatibleLLMClient.generate_task_plan` - 2 calls
- `src.nxdo.ticket_generator.task_plan_to_tickets` - 2 calls
- `src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan` - 2 calls
- `src.nxdo.config.get_settings` - 1 calls
- `src.nxdo.cli.app_entry` - 1 calls
- `src.nxdo.llm_client.build_user_prompt` - 1 calls
- `src.nxdo.llm_client.parse_task_plan_response` - 1 calls
- `src.nxdo.models.Task.to_dict` - 1 calls
- `src.nxdo.models.TaskPlan.to_dict` - 1 calls
- `src.nxdo.koru_context.get_koru_system_prompt_extension` - 0 calls
- `src.nxdo.providers.base.LLMProvider.generate_plan` - 0 calls
- `src.nxdo.metrics.complexity.get_high_complexity_files` - 0 calls
- `src.nxdo.metrics.complexity.get_poorly_typed_files` - 0 calls

## System Interactions

How components interact:

```mermaid
graph TD
    cmd_metrics --> command
    cmd_metrics --> Argument
    cmd_metrics --> Option
    cmd_metrics --> resolve
    cmd_auto --> command
    cmd_auto --> Argument
    cmd_auto --> Option
    cmd_auto --> resolve
    cmd_tickets --> command
    cmd_tickets --> Argument
    cmd_tickets --> Option
    main --> ArgumentParser
    main --> add_argument
    cmd_plan --> command
    cmd_plan --> Argument
    cmd_plan --> Option
    cmd_print_context --> command
    cmd_print_context --> Argument
    cmd_print_context --> Option
    cmd_print_context --> analyze_project
    cmd_print_prompt --> command
    cmd_print_prompt --> Argument
    cmd_print_prompt --> Option
    cmd_print_prompt --> analyze_project
    _call_api --> retry
    _call_api --> ValueError
    _call_api --> get_koru_system_prom
    _call_api --> Client
    _call_api --> post
    __str__ --> join
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.