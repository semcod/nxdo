# Changelog

## [Unreleased]

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
