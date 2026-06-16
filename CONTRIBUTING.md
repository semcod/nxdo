# Contributing to nxdo

Thank you for your interest in contributing to `nxdo`!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/semcod/nxdo.git
cd nxdo
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e ".[dev]"
```

## Running Tests

Run all tests:
```bash
PYTHONPATH=src python -m pytest tests/ -v
```

Run a specific test file:
```bash
PYTHONPATH=src python -m pytest tests/test_models.py -v
```

## Code Quality

Run type checking:
```bash
mypy src/nxdo
```

Run linting:
```bash
ruff check src/nxdo tests/
```

Auto-fix linting issues:
```bash
ruff check --fix src/nxdo tests/
```

## Project Structure

- `src/nxdo/` - Main package source code
  - `cli.py` - Command-line interface
  - `config.py` - Configuration management
  - `git_reader.py` - Git history analysis
  - `llm_client.py` - LLM client (legacy compatibility)
  - `models.py` - Pydantic data models
  - `output.py` - Rich-based rendering
  - `planner.py` - Main orchestrator
  - `project_analyzer.py` - Project snapshot analysis
  - `providers/` - LLM provider implementations
- `tests/` - Test suite

## Making Changes

1. Create a branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and add tests
3. Run tests and linting to ensure everything passes
4. Commit your changes with a clear message
5. Push and create a pull request

## Adding New LLM Providers

To add a new LLM provider:

1. Create a new file in `src/nxdo/providers/`
2. Implement the `LLMProvider` interface from `providers/base.py`
3. Add appropriate tests in `tests/test_providers.py`
4. Export the provider in `src/nxdo/providers/__init__.py`

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
