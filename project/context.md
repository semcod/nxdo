# System Architecture Analysis
<!-- generated in 0.00s -->

## Overview

- **Project**: /home/tom/github/semcod/nxdo
- **Primary Language**: python
- **Languages**: python: 21, yaml: 7, txt: 6, shell: 2, toml: 1
- **Analysis Mode**: static
- **Total Functions**: 150
- **Total Classes**: 26
- **Modules**: 37
- **Entry Points**: 41

## Architecture by Module

### src.nxdo.git_reader
- **Functions**: 19
- **Classes**: 2
- **File**: `git_reader.py`

### src.nxdo.project_analyzer
- **Functions**: 19
- **Classes**: 1
- **File**: `project_analyzer.py`

### src.nxdo.providers.openai_compat
- **Functions**: 18
- **Classes**: 3
- **File**: `openai_compat.py`

### nxdo.metrics.complexity
- **Functions**: 18
- **Classes**: 4
- **File**: `complexity.py`

### src.nxdo.cli
- **Functions**: 16
- **Classes**: 1
- **File**: `cli.py`

### src.nxdo.ticket_generator
- **Functions**: 13
- **File**: `ticket_generator.py`

### src.nxdo.metrics.hotspots
- **Functions**: 10
- **Classes**: 2
- **File**: `hotspots.py`

### src.nxdo.koru_context
- **Functions**: 6
- **Classes**: 3
- **File**: `koru_context.py`

### src.nxdo.metrics.coupling
- **Functions**: 5
- **Classes**: 1
- **File**: `coupling.py`

### examples.check-examples
- **Functions**: 4
- **File**: `check-examples.sh`

### src.nxdo.output
- **Functions**: 4
- **File**: `output.py`

### src.nxdo.llm_client
- **Functions**: 4
- **Classes**: 1
- **File**: `llm_client.py`

### src.nxdo.models
- **Functions**: 4
- **Classes**: 4
- **File**: `models.py`

### scripts.check_import_layers
- **Functions**: 4
- **File**: `check_import_layers.py`

### nxdo.text_builder
- **Functions**: 3
- **Classes**: 1
- **File**: `text_builder.py`

### src.nxdo.config
- **Functions**: 1
- **Classes**: 1
- **File**: `config.py`

### src.nxdo.planner
- **Functions**: 1
- **File**: `planner.py`

### src.nxdo.providers.base
- **Functions**: 1
- **Classes**: 2
- **File**: `base.py`

## Key Entry Points

Main execution flows into the system:

### src.nxdo.cli.cmd_metrics
> Display code metrics: complexity, coupling, hotspots.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, repo.resolve, console.print, console.print, nxdo.metrics.complexity.collect_file_metrics

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

### src.nxdo.cli.cmd_print_context
> Print the assembled project and git context (no LLM call).
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, src.nxdo.project_analyzer.analyze_project, src.nxdo.git_reader.read_git_context, snapshot.to_text, git_ctx.to_text

### src.nxdo.cli.cmd_plan
> Generate a 10-task plan for the repository.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, typer.Option, typer.Option, typer.Option, src.nxdo.cli._generate_plan

### src.nxdo.models.TaskPlan.__str__
- **Calls**: LineBuilder, builder.text, builder.line, builder.line, builder.line, builder.line, str, builder.line

### scripts.check_import_layers.main
- **Calls**: sorted, examples.check-examples.print, PACKAGE_ROOT.rglob, scripts.check_import_layers.module_name, violations.extend, examples.check-examples.print, violations.append, scripts.check_import_layers.check_file

### src.nxdo.git_reader.GitContext.to_text
- **Calls**: LineBuilder, builder.line, builder.text, builder.line, builder.line, builder.line, builder.line, builder.line

### src.nxdo.cli.cmd_validate
> Validate a saved JSON plan file against the TaskPlan schema.
- **Calls**: app.command, typer.Argument, console.print, json.loads, TaskPlan.model_validate, plan_file.read_text, err_console.print, typer.Exit

### src.nxdo.providers.openai_compat.OpenAICompatProvider._call_api
- **Calls**: retry, self._post_chat, self._parse_success_json, src.nxdo.providers.openai_compat._extract_content, LLMAPIError, self._http_error, retry_if_exception_type, stop_after_attempt

### src.nxdo.cli.cmd_print_prompt
> Print the full prompt that would be sent to the LLM.
- **Calls**: app.command, typer.Argument, typer.Option, typer.Option, PromptInputs, examples.check-examples.print, Path, src.nxdo.cli._render_prompt_text

### src.nxdo.project_analyzer.ProjectSnapshot.to_text
- **Calls**: LineBuilder, self.file_contents.items, builder.text, builder.line, builder.line, None.join

### src.nxdo.metrics.hotspots.get_critical_bus_factor_files
> Get files with critical bus factor (1-2 authors) + their authors.

Returns:
    [(file_path, author_count, [author_names]), ...]
- **Calls**: bus_factors.items, critical.sort, src.nxdo.metrics.hotspots.calculate_bus_factor, src.nxdo.metrics.hotspots._get_file_authors, critical.append

### src.nxdo.providers.openai_compat.OpenAICompatProvider._post_chat
- **Calls**: httpx.Client, client.post, self._build_payload, self._build_headers

### src.nxdo.git_reader.CommitInfo.__str__
- **Calls**: None.join, len, len

### src.nxdo.llm_client.OpenAICompatibleLLMClient.__init__
- **Calls**: OpenAICompatProvider, os.environ.get, os.environ.get

### src.nxdo.llm_client.OpenAICompatibleLLMClient.generate_task_plan
- **Calls**: src.nxdo.llm_client.build_user_prompt, self._provider.generate_plan, PlanRequest

### src.nxdo.models.Task.__str__
- **Calls**: self.task_type.value.upper, int, int

### src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan
- **Calls**: self._call_api, src.nxdo.providers.openai_compat._parse_response, ResponseInputs

### src.nxdo.providers.openai_compat.OpenAICompatProvider._http_error
- **Calls**: src.nxdo.providers.openai_compat._extract_error_detail, src.nxdo.providers.openai_compat._http_status_hint, LLMAPIError

### src.nxdo.llm_client.parse_task_plan_response
> Parse a raw JSON string from the LLM into a TaskPlan. (Compatibility wrapper.)
- **Calls**: src.nxdo.providers.openai_compat._parse_response, ResponseInputs

### src.nxdo.providers.openai_compat.LLMAPIError.__init__
- **Calls**: None.__init__, super

### src.nxdo.providers.openai_compat.OpenAICompatProvider.__init__
- **Calls**: None.rstrip, src.nxdo.config.get_settings

### src.nxdo.providers.openai_compat.OpenAICompatProvider._build_headers
- **Calls**: os.getenv, os.getenv

### src.nxdo.providers.openai_compat.OpenAICompatProvider._parse_success_json
- **Calls**: response.json, LLMAPIError

### src.nxdo.cli.app_entry
> Entry point used by the installed `nxdo` script.
- **Calls**: app

### nxdo.text_builder.LineBuilder.__init__
- **Calls**: list

### nxdo.text_builder.LineBuilder.line
> Append one or more lines.
- **Calls**: self._lines.extend

### nxdo.text_builder.LineBuilder.text
> Return the accumulated lines joined with newlines.
- **Calls**: None.join

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

### Flow 5: cmd_print_context
```
cmd_print_context [src.nxdo.cli]
  └─ →> analyze_project
      └─> _collect_file_contents
          └─> _read_file_safely
          └─> _truncate_file_content
```

### Flow 6: cmd_plan
```
cmd_plan [src.nxdo.cli]
```

### Flow 7: __str__
```
__str__ [src.nxdo.models.TaskPlan]
```

### Flow 8: to_text
```
to_text [src.nxdo.git_reader.GitContext]
```

### Flow 9: cmd_validate
```
cmd_validate [src.nxdo.cli]
```

### Flow 10: _call_api
```
_call_api [src.nxdo.providers.openai_compat.OpenAICompatProvider]
  └─ →> _extract_content
```

## Key Classes

### src.nxdo.providers.openai_compat.OpenAICompatProvider
> Provider for OpenRouter or any OpenAI-compatible endpoint.
- **Methods**: 10
- **Key Methods**: src.nxdo.providers.openai_compat.OpenAICompatProvider.__init__, src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan, src.nxdo.providers.openai_compat.OpenAICompatProvider._chat_endpoint, src.nxdo.providers.openai_compat.OpenAICompatProvider._call_api, src.nxdo.providers.openai_compat.OpenAICompatProvider._build_system_prompt, src.nxdo.providers.openai_compat.OpenAICompatProvider._build_payload, src.nxdo.providers.openai_compat.OpenAICompatProvider._build_headers, src.nxdo.providers.openai_compat.OpenAICompatProvider._post_chat, src.nxdo.providers.openai_compat.OpenAICompatProvider._http_error, src.nxdo.providers.openai_compat.OpenAICompatProvider._parse_success_json
- **Inherits**: LLMProvider

### nxdo.text_builder.LineBuilder
> Single owner of the line-list mutation used to assemble text blocks.
- **Methods**: 3
- **Key Methods**: nxdo.text_builder.LineBuilder.__init__, nxdo.text_builder.LineBuilder.line, nxdo.text_builder.LineBuilder.text

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

### src.nxdo.providers.openai_compat.LLMAPIError
> An LLM API failure with structured, actionable detail.

Subclasses :class:`ValueError` so existing c
- **Methods**: 1
- **Key Methods**: src.nxdo.providers.openai_compat.LLMAPIError.__init__
- **Inherits**: ValueError

### src.nxdo.cli.PromptInputs
> Repository, extra context and history depth needed to assemble an LLM prompt.
- **Methods**: 0

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

### src.nxdo.providers.base.PlanRequest
> User prompt plus project identity forwarded together to the LLM backend.
- **Methods**: 0

### src.nxdo.providers.openai_compat.ResponseInputs
> Raw LLM response text plus the metadata needed to parse it into a TaskPlan.
- **Methods**: 0

### nxdo.metrics.complexity.LineCounts
> Line tallies for a single source file.
- **Methods**: 0
- **Inherits**: NamedTuple

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
- **Output to**: src.nxdo.providers.openai_compat._parse_response, ResponseInputs

### src.nxdo.koru_context._format_operations_for_llm
> Format koru operations as structured text for LLM prompt.
- **Output to**: ops_lines.append, sorted, None.join, None.append, by_domain.items

### src.nxdo.koru_context._format_project_state_for_llm
> Format current koru project state for LLM prompt.
- **Output to**: state_lines.append, state_lines.append, state_lines.append, state_lines.append, None.join

### src.nxdo.project_analyzer._parse_pyproject_tomllib
> Parse pyproject.toml using tomllib if available.
- **Output to**: parsed.get, isinstance, tomllib.loads, project.get, project.get

### src.nxdo.project_analyzer._parse_pyproject_regex
> Parse pyproject.toml using regex fallback.
- **Output to**: re.search, re.search, name_match.group, description_match.group

### src.nxdo.project_analyzer._parse_pyproject
- **Output to**: src.nxdo.project_analyzer._parse_pyproject_tomllib, src.nxdo.project_analyzer._parse_pyproject_regex

### src.nxdo.project_analyzer._parse_package_json
- **Output to**: json.loads, package_json.get, package_json.get, path.read_text

### src.nxdo.project_analyzer._parse_cargo
- **Output to**: re.search, re.search, name_match.group, description_match.group

### src.nxdo.providers.openai_compat.OpenAICompatProvider._parse_success_json
- **Output to**: response.json, LLMAPIError

### src.nxdo.providers.openai_compat._parse_json_response
> Parse JSON from raw response with error handling.
- **Output to**: json.loads, isinstance, ValueError, ValueError, type

### src.nxdo.providers.openai_compat._parse_tasks_from_data
> Parse tasks from the parsed plan JSON.
- **Output to**: enumerate, plan_json.get, tasks.append, src.nxdo.providers.openai_compat._create_task_from_dict

### src.nxdo.providers.openai_compat._parse_response
> Parse and validate the raw JSON response from the LLM.
- **Output to**: src.nxdo.providers.openai_compat._strip_markdown_fences, src.nxdo.providers.openai_compat._parse_json_response, src.nxdo.providers.openai_compat._parse_tasks_from_data, TaskPlan, plan_json.get

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `src.nxdo.cli.cmd_metrics` - 33 calls
- `src.nxdo.cli.cmd_auto` - 30 calls
- `src.nxdo.cli.cmd_tickets` - 25 calls
- `src.nxdo.cli.main` - 21 calls
- `scripts.check_import_layers.check_file` - 15 calls
- `src.nxdo.cli.cmd_print_context` - 14 calls
- `src.nxdo.output.render_plan` - 14 calls
- `src.nxdo.cli.cmd_plan` - 13 calls
- `src.nxdo.ticket_generator.sync_to_planfile` - 13 calls
- `src.nxdo.metrics.coupling.get_coupling_clusters` - 13 calls
- `scripts.check_import_layers.main` - 12 calls
- `src.nxdo.git_reader.GitContext.to_text` - 10 calls
- `src.nxdo.planner.generate_next_tasks` - 10 calls
- `src.nxdo.cli.cmd_validate` - 9 calls
- `src.nxdo.cli.cmd_print_prompt` - 8 calls
- `src.nxdo.git_reader.read_git_context` - 8 calls
- `src.nxdo.koru_context.build_koru_context` - 8 calls
- `src.nxdo.metrics.coupling.collect_coupling_matrix` - 7 calls
- `scripts.check_import_layers.resolve_import` - 7 calls
- `src.nxdo.ticket_generator.sync_to_todo_md` - 6 calls
- `src.nxdo.project_analyzer.ProjectSnapshot.to_text` - 6 calls
- `src.nxdo.output.render_context` - 5 calls
- `src.nxdo.project_analyzer.analyze_project` - 5 calls
- `src.nxdo.metrics.hotspots.get_critical_bus_factor_files` - 5 calls
- `src.nxdo.output.render_plan_json` - 4 calls
- `src.nxdo.ticket_generator.export_to_planfile_yaml` - 4 calls
- `nxdo.metrics.complexity.collect_file_metrics` - 4 calls
- `src.nxdo.metrics.hotspots.identify_bug_hotspots` - 4 calls
- `src.nxdo.metrics.hotspots.calculate_bus_factor` - 4 calls
- `scripts.check_import_layers.module_name` - 4 calls
- `src.nxdo.llm_client.OpenAICompatibleLLMClient.generate_task_plan` - 3 calls
- `src.nxdo.providers.openai_compat.OpenAICompatProvider.generate_plan` - 3 calls
- `src.nxdo.config.get_settings` - 2 calls
- `src.nxdo.llm_client.parse_task_plan_response` - 2 calls
- `src.nxdo.ticket_generator.task_plan_to_tickets` - 2 calls
- `src.nxdo.cli.app_entry` - 1 calls
- `src.nxdo.llm_client.build_user_prompt` - 1 calls
- `nxdo.text_builder.LineBuilder.line` - 1 calls
- `nxdo.text_builder.LineBuilder.text` - 1 calls
- `src.nxdo.models.Task.to_dict` - 1 calls

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
    cmd_print_context --> command
    cmd_print_context --> Argument
    cmd_print_context --> Option
    cmd_print_context --> analyze_project
    cmd_plan --> command
    cmd_plan --> Argument
    cmd_plan --> Option
    __str__ --> LineBuilder
    __str__ --> text
    __str__ --> line
    main --> sorted
    main --> print
    main --> rglob
    main --> module_name
    main --> extend
    to_text --> LineBuilder
    to_text --> line
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.