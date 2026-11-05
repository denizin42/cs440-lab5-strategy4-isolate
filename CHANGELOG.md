# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Keep a Changelog (`CHANGELOG.md`) enforcement in `.githooks/pre-commit` and Claude `PreToolUse` hook.
- Helper script `scripts/changelog-add.sh` for appending entries under `## [Unreleased]` and staging `CHANGELOG.md`.
- Multi-agent teammate onboarding script (`scripts/setup-teammate.sh`) and `TEAM_ONBOARDING.md`.
- On-demand `github-kanban-sync` Claude Code skill and combined `KANBAN_BOARD.md`.
- Git `pre-commit` and Claude `PreToolUse` hooks blocking direct commits to `main`.

### Changed
- Differentiated `CLAUDE.md` and `README.md` between Strategy 1 (Write) and Strategy 4 (Isolate).
- Configured `.vscode/settings.json` and `pytest.ini` (`--import-mode=importlib`) for VS Code Test Explorer discovery.

### Removed
- Removed pre-written Python solution files in `src/` so the AI agent generates `src/` from the Context Engineering markdown instructions.

## [0.1.0] - 2026-11-03

### Added
- Initial CS 440 Lab 5 repository scaffolding with Hooks, MCP (`mcp_server.py`), Skills, and Sub-agents.
