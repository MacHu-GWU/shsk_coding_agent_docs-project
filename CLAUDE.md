# Project Guide for AI Assistants

This document guides AI assistants on how to navigate and work with this project.

## Project Overview

**What this project does:** Distills the official documentation of AI coding agents into reusable Agent Skills, so an agent can discover, organize, and learn from another tool's current docs on demand — instead of relying on stale training data or assumptions. Targets three agents today: Anthropic's Claude Code, OpenAI's Codex, and Google's Antigravity. Everything meant for external use ships as a single Claude Code plugin, `coding-agent-docs`, under `.claude/skills/coding-agent-docs/`. See `README.rst` and `docs/source/99-Maintainer-Guide/` for details.

**Project type:** Python package housing a Claude Code plugin

## Core Configuration Files

### Tool & Dependency Management
- `mise.toml` - Task runner and tool version management (Python 3.12, uv, claude)
- `pyproject.toml` - Python dependencies and package metadata
- `.venv/` - Virtual environment directory (created by uv)

Use `mise ls python --current` to see the exact Python version in use.

### CI/CD & Testing
- `.github/workflows/main.yml` - GitHub Actions CI workflow
- `codecov.yml` + `.coveragerc` - Code coverage reporting (codecov.io)
- `.readthedocs.yml` - Documentation hosting (readthedocs.org)

### Documentation
- `docs/source/` - Sphinx documentation source files
- `docs/source/conf.py` - Sphinx configuration

## Development Workflow

### Task Management
List all available tasks:
```bash
mise tasks ls
```

Run a specific task:
```bash
mise run ${task_name}
```

**Key tasks:**
- `inst` - Install all dependencies using uv (fast package manager)
- `cov` - Run unit tests with coverage report
- `build-doc` - Build Sphinx documentation

For complete task reference, run `mise run list-tasks` to generate `.claude/mise-tasks.md`.

### Testing Philosophy
This project uses **pytest** with a special pattern that allows running individual test files as standalone scripts.

**Example:** See `tests/test_api.py` - the `if __name__ == "__main__":` block demonstrates this pattern. It runs pytest as a subprocess with coverage tracking for the specific module, enabling quick isolated testing during development.

## Working with This Project

**Approach:**
1. Don't load entire files unnecessarily - read specific files only when needed
2. Use task commands (`mise run`) instead of direct tool invocation
3. Follow the testing pattern when creating new test files
4. Reference configuration files for specific settings rather than assuming defaults

**Tools in use:**
- **mise-en-place** - Development tool management
- **uv** - Fast Python package management
- **pytest** - Unit testing framework
- **sphinx** - Documentation generation
