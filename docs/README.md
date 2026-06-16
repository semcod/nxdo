# nxdo documentation

| Document | Description |
|----------|-------------|
| [How it works](./how-it-works.md) | End-to-end pipeline, step-by-step walkthrough, troubleshooting |
| [Examples](../examples/) | Real `print-context`, `metrics`, and `plan` outputs from the nxdo repo |
| [CLI reference](../README.md#cli-reference) | All commands and flags |
| [Configuration](../README.md#configuration) | Environment variables |
| [Contributing](../CONTRIBUTING.md) | Development setup and tests |
| [Changelog](../CHANGELOG.md) | Release history |

Quick start:

```bash
pip install nxdo
nxdo print-context .
nxdo plan . -e "What should we build next?"
```
