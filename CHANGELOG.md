# Changelog

## [Unreleased]

## [0.2.11] - 2026-05-26

### Docs
- Update README.md
- Update TODO.md

### Test
- Update tests/test_cli.py

### Other
- Update .koru/events/observability.jsonl
- Update .planfile/sprints/current.yaml
- Update project/planfile-tickets.yaml

## [0.2.10] - 2026-05-26

### Docs
- Update README.md
- Update TODO.md

### Test
- Update tests/test_cli.py
- Update tests/test_project_analyzer.py
- Update tests/test_providers.py
- Update tests/test_ticket_generator.py

### Other
- Update .planfile/.store.lock
- Update .planfile/sprints/current.yaml
- Update strategy.yaml
- Update uv.lock

## [0.2.9] - 2026-05-26

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md

### Test
- Update tests/test_cli.py
- Update tests/test_config.py
- Update tests/test_providers.py

### Other
- Update app.doql.less
- Update project/calls.png
- Update project/duplication.toon.yaml
- Update project/flow.png
- Update project/index.html
- Update project/logic.pl
- Update project/map.toon.yaml
- Update project/project.toon.yaml

## [0.2.9] - 2026-05-26

### Fixed
- Fix .env file loading - add automatic .env loading via pydantic-settings
- Fix 400 Bad Request error from OpenRouter - change model to openai/gpt-4o-mini
- Fix API error handling - add detailed error messages for API failures
- Fix dependencies parsing - handle string dependencies by filtering/converting to integers
- Update tests to disable .env loading in test scenarios

### Changed
- Change default model from openrouter/qwen/qwen3-coder-next to openai/gpt-4o-mini
- Update config.py to load .env file automatically

## [0.2.8] - 2026-05-26

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/__init___1779813747840622603_823.pkl
- Update .code2llm_cache/cli_1779813728398420144_8551.pkl
- Update .code2llm_cache/pyproject_1779813746964613479_2251.pkl
- Update .code2llm_cache/ticket_generator_1779813709436222750_5067.pkl
- Update .code2llm_cache/tree_1779813839904582136_1756.pkl
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- ... and 14 more files

## [0.2.7] - 2026-05-26

### New
- Add planfile integration for ticket generation
- Add `lane tickets` CLI command with planfile support
- Add ticket_generator module with TaskPlan to planfile conversion
- Add `--sync-todo` flag to sync tasks to TODO.md checkboxes
- Add `--export-yaml` flag to export to planfile YAML format

### Changed
- Add pyyaml as runtime dependency
- Add planfile as local path dependency for ticket generation features

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md

### Test
- Add tests/test_ticket_generator.py with ticket generation tests

### Other
- Update app.doql.less
- Update project/logic.pl
- Update project/map.toon.yaml
- Update uv.lock

## [0.2.6] - 2026-05-26

### Refactor
- Remove code duplication in git_reader.py - extract _run_git_command helper
- Remove code duplication in project_analyzer.py - extract _get_tree_symbol helper
- Refactor _parse_pyproject (CC=6 → CC=4) - extract _parse_pyproject_tomllib and _parse_pyproject_regex
- Refactor _detect_stack (CC=6 → CC=4) - extract _check_pattern_match helper
- Refactor _resolve_name_and_description (CC=5 → CC=3) - use data-driven approach
- Refactor _collect_file_contents (CC=5 → CC=4) - extract _truncate_file_content helper
- Refactor _get_file_frequency (CC=4 → CC=1) - extract _count_file_frequencies and _format_file_summary helpers
- Improve overall code complexity: CC̄=3.7 → CC̄=2.6

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/__init___1779813089818599765_823.pkl
- Update .code2llm_cache/pyproject_1779813089323595748_2093.pkl
- Update app.doql.less
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.png
- Update project/duplication.toon.yaml
- ... and 10 more files

## [0.2.5] - 2026-05-26

### Docs
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md

### Other
- Update .code2llm_cache/__init___1779812250483313022_823.pkl
- Update .code2llm_cache/__init___1779812598110645593_823.pkl
- Update .code2llm_cache/generated-cli-tests.testql.toon_1779812133581462729_428.pkl
- Update .code2llm_cache/generated-from-pytests.testql.toon_1779812133581379073_328.pkl
- Update .code2llm_cache/git_reader_1779812433507912682_5973.pkl
- Update .code2llm_cache/git_reader_1779813058356493831_6556.pkl
- Update .code2llm_cache/goal_1779812236774842677_12261.pkl
- Update .code2llm_cache/openai_compat_1779812443457017403_6021.pkl
- Update .code2llm_cache/project_analyzer_1779812419570765990_7032.pkl
- Update .code2llm_cache/project_analyzer_1779813050876415013_7979.pkl
- ... and 21 more files

## [0.2.4] - 2026-05-26

### Docs
- Update README.md

### Test
- Update tests/test_cli.py

## [0.2.3] - 2026-05-26

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update project/README.md
- Update project/context.md
- Update todo.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update testql-scenarios/generated-from-pytests.testql.toon.yaml

### Other
- Update .code2llm_cache/__init___1779809524215187208_172.pkl
- Update .code2llm_cache/__init___1779812002217425058_823.pkl
- Update .code2llm_cache/__main___1779808740120530743_81.pkl
- Update .code2llm_cache/base_1779809524215844720_438.pkl
- Update .code2llm_cache/cli_1779809524215187208_5928.pkl
- Update .code2llm_cache/config_1779809524215187208_1120.pkl
- Update .code2llm_cache/git_reader_1779809524215187208_4761.pkl
- Update .code2llm_cache/goal_1779811976473106769_12258.pkl
- Update .code2llm_cache/llm_client_1779809524215187208_2431.pkl
- Update .code2llm_cache/models_1779809524215187208_2579.pkl
- ... and 27 more files

## [0.2.2] - 2026-05-26

### Added
- Author: Tom Sapletta (tom@sapletta.com)
- Development dependencies: goal, costs, pfix
- AI tools configuration (pfix, costs) in pyproject.toml
- AI cost tracking badges in README
- Updated version to 0.2.2

### Changed
- Updated AI cost tracking information
- Cleaned up README formatting

## [0.2.1] - 2026-05-26

### Docs
- Update CHANGELOG.md
- Update CONTRIBUTING.md
- Update README.md
- Update todo.md

### Test
- Update tests/test_cli.py
- Update tests/test_git_reader.py
- Update tests/test_llm_client.py
- Update tests/test_models.py
- Update tests/test_output.py
- Update tests/test_planner.py
- Update tests/test_project_analyzer.py
- Update tests/test_providers.py

### Other
- Update .env.example
- Update .idea/.gitignore
- Update .idea/inspectionProfiles/Project_Default.xml
- Update .idea/inspectionProfiles/profiles_settings.xml
- Update .idea/lane.iml
- Update .idea/modules.xml
- Update .idea/pyProjectModel.xml
- Update .idea/vcs.xml
- Update MANIFEST.in
- Update project.sh
- ... and 2 more files


All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-05-26

### Added
- CLI Reference section in README with detailed command documentation
- Comprehensive test suite with 96% code coverage (80 tests)
- CONTRIBUTING.md guide for developers
- Examples section in README with practical usage patterns
- Tests for all major modules (output, planner, git_reader, project_analyzer, llm_client, providers)
- Typer CliRunner tests for direct command testing
- Mock-based tests for LLM provider interactions

### Changed
- Improved project_analyzer.py coverage to 95%
- Improved git_reader.py coverage to 100%
- Improved CLI coverage to 89%
- Enhanced documentation for all CLI commands

### Fixed
- Fixed test coverage gaps in multiple modules
- Improved error handling tests

## [0.1.0] - 2026-05-26

### Added
- Initial release of lane
- Project snapshot analysis (README, manifests, directory tree, stack detection)
- Git context extraction (commits, changed files, TODO/FIXME markers)
- Pydantic models for tasks and plans
- Provider abstraction with OpenAI-compatible provider
- Rich CLI with `lane plan`, `lane print-context`, `lane print-prompt`, `lane validate`
- HTTP reliability with httpx and tenacity retry/backoff
- Environment-based configuration with pydantic-settings
