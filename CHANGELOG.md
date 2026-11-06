# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Resolved all pylint warnings in mcp_server.py and tests/test_lab5_progress.py (10.00/10)

### Added
- Add zero-prompt autonomous demo protocol in CLAUDE.md, AGENTS.md symlink, pre-approved tool permissions in .claude/settings.json, and scripts/demo-reset.sh
- Completed all Context Engineering tests (22/22 green) and updated KANBAN_BOARD.md
- Finished setup of CLAUDE.md file and mcp server and skill and subagents to get all tests green
- Added GitHub Actions Pylint CI workflow (.github/workflows/pylint.yml)
- fixed tests for setting up idempotency guard for loading resources, setup CLAUDE settings.json to include the new hook for context switching from prompts
- Keep a Changelog (`CHANGELOG.md`) enforcement in `.githooks/pre-commit` and Claude `PreToolUse` hook.
- Helper script `scripts/changelog-add.sh` for appending entries under `## [Unreleased]` and staging `CHANGELOG.md`.
- Multi-agent teammate onboarding script (`scripts/setup-teammate.sh`) and `TEAM_ONBOARDING.md`.
- On-demand `github-kanban-sync` Claude Code skill and combined `KANBAN_BOARD.md`.
- Git `pre-commit` and Claude `PreToolUse` hooks blocking direct commits to `main`.

### Changed
- Update CLAUDE.md autonomous zero-prompt protocol to include the 4-dimensional hyperparameter sensitivity sweep
- Differentiated `CLAUDE.md` and `README.md` between Strategy 1 (Write) and Strategy 4 (Isolate).
- Configured `.vscode/settings.json` and `pytest.ini` (`--import-mode=importlib`) for VS Code Test Explorer discovery.

### Removed
- Removed pre-written Python solution files in `src/` so the AI agent generates `src/` from the Context Engineering markdown instructions.

## [0.1.0] - 2026-11-03

### Added
- Initial CS 440 Lab 5 repository scaffolding with Hooks, MCP (`mcp_server.py`), Skills, and Sub-agents.
