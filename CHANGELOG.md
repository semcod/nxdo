# Changelog

## [Unreleased]

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
