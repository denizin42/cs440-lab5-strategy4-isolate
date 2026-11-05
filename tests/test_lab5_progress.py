"""CS 440 Lab 5 Context Engineering Verification Test Suite.

Verifies the human-configured Context Engineering files (CLAUDE.md, Hooks, Skills,
Sub-Agents, and MCP Server) BEFORE the AI agent generates the Python solution in `src/`.

Run all checks:
    pytest -v
"""
# pylint: disable=too-few-public-methods,import-error,wrong-import-position

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mcp_server import (  # noqa: E402
    audit_hyperparameters_prompt,
    get_hyperparameters_resource,
    verify_hyperparameters,
)


class TestPart1HyperparametersInMarkdown:
    """Verifies Part 1: Selected Hyperparameters are documented in `CLAUDE.md`."""

    def test_part_1_hyperparameters_documented_in_claude_md(self) -> None:
        """Verify `CLAUDE.md` specifies all 4 Q-learning hyperparameters."""
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "TODO_SET_VALUE" not in claude_md.split("-->")[-1], (
            "TODO Part 1: Set all 4 hyperparameter values in the CLAUDE.md table"
        )
        for param_name in (
            "living_reward",
            "discount_gamma",
            "learning_rate_alpha",
            "exploration_epsilon",
        ):
            assert param_name in claude_md


class TestPart2HooksAndMemory:
    """Verifies Feature 1: Hooks (.claude/settings.json, scripts/context-switcher.sh)."""

    def test_pre_commit_hook_blocks_main_branch(self) -> None:
        """Verify pre-commit and PreToolUse hooks block `main` and enforce changelog."""
        git_hook = REPO_ROOT / ".githooks" / "pre-commit"
        claude_pre_hook = REPO_ROOT / "scripts" / "prevent-main-commit.sh"
        changelog_file = REPO_ROOT / "CHANGELOG.md"
        changelog_helper = REPO_ROOT / "scripts" / "changelog-add.sh"
        settings_path = REPO_ROOT / ".claude" / "settings.json"

        assert git_hook.exists(), ".githooks/pre-commit must exist"
        assert claude_pre_hook.exists(), "scripts/prevent-main-commit.sh must exist"
        assert changelog_file.exists(), "CHANGELOG.md must exist"
        assert changelog_helper.exists(), "scripts/changelog-add.sh must exist"

        hook_text = git_hook.read_text(encoding="utf-8")
        assert "Direct commits to" in hook_text
        assert "CHANGELOG.md" in hook_text and "Keep a Changelog" in hook_text

        changelog_text = changelog_file.read_text(encoding="utf-8")
        assert "# Changelog" in changelog_text and "## [Unreleased]" in changelog_text

        data = json.loads(settings_path.read_text(encoding="utf-8"))
        pre_tool_cmd = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert "scripts/prevent-main-commit.sh" in pre_tool_cmd

    def test_part_2a_settings_json_hook_registered(self) -> None:
        """Verify `.claude/settings.json` registers `scripts/context-switcher.sh`."""
        settings_path = REPO_ROOT / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        command = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        assert "TODO" not in command, (
            "TODO Part 2A: Set the hook command in .claude/settings.json"
        )
        assert "scripts/context-switcher.sh" in command

    def test_part_2b_context_switcher_idempotency_guard(self) -> None:
        """Verify `scripts/context-switcher.sh` uses `grep -qxF` idempotency guard."""
        script_path = REPO_ROOT / "scripts" / "context-switcher.sh"
        script_text = script_path.read_text(encoding="utf-8")
        assert "grep -qxF" in script_text, (
            "TODO Part 2B: Use grep -qxF inside add_context()"
        )
        assert "return 1" not in script_text, (
            "TODO Part 2B: Remove placeholder `return 1` in add_context()"
        )

    def test_part_2c_claude_md_dynamic_context_imports(self) -> None:
        """Verify `CLAUDE.md` contains uncommented `@./context/*.md` imports."""
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        active_lines = [
            line
            for line in claude_md.splitlines()
            if line.startswith("@./context/")
        ]
        assert "@./context/environment.md" in active_lines, (
            "TODO Part 2C: Add @./context/environment.md at start of line in CLAUDE.md"
        )
        assert "@./context/q-learning.md" in active_lines, (
            "TODO Part 2C: Add @./context/q-learning.md at start of line in CLAUDE.md"
        )
        assert "@./context/exploration.md" in active_lines, (
            "TODO Part 2C: Add @./context/exploration.md at start of line in CLAUDE.md"
        )


class TestPart3Skills:
    """Verifies Feature 3: On-Demand Skill (`.claude/skills/q-learning-audit/SKILL.md`)."""

    def test_part_3_skill_frontmatter(self) -> None:
        """Verify `.claude/skills/q-learning-audit/SKILL.md` defines valid frontmatter."""
        skill_text = (
            REPO_ROOT / ".claude" / "skills" / "q-learning-audit" / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert "TODO_PART_3" not in skill_text, (
            "TODO Part 3: Fill in name and description in SKILL.md"
        )
        assert "name: q-learning-audit" in skill_text


class TestPart4SubAgents:
    """Verifies Feature 4: Isolated Sub-Agents (`.claude/agents/*.md` and `CLAUDE.md`)."""

    def test_part_4a_subagent_yaml_frontmatter(self) -> None:
        """Verify `code-reviewer.md` and `researcher.md` have complete frontmatter."""
        reviewer_path = REPO_ROOT / ".claude" / "agents" / "code-reviewer.md"
        researcher_path = REPO_ROOT / ".claude" / "agents" / "researcher.md"
        reviewer_text = reviewer_path.read_text(encoding="utf-8")
        researcher_text = researcher_path.read_text(encoding="utf-8")

        assert "TODO_PART_4A" not in reviewer_text, (
            "TODO Part 4A: Complete frontmatter in code-reviewer.md"
        )
        assert "name: code-reviewer" in reviewer_text
        assert '"Read"' in reviewer_text and '"Grep"' in reviewer_text

        assert "TODO_PART_4A" not in researcher_text, (
            "TODO Part 4A: Complete frontmatter in researcher.md"
        )
        assert "name: researcher" in researcher_text
        assert '"Read"' in researcher_text and '"Grep"' in researcher_text

    def test_part_4b_claude_md_task_delegation(self) -> None:
        """Verify `CLAUDE.md` delegates to `code-reviewer` and `researcher`."""
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "TODO_SET_REVIEWER_SUBAGENT" not in claude_md, (
            "TODO Part 4B: Set code-reviewer in CLAUDE.md"
        )
        assert "TODO_SET_RESEARCHER_SUBAGENT" not in claude_md, (
            "TODO Part 4B: Set researcher in CLAUDE.md"
        )
        assert 'subagent_type: "code-reviewer"' in claude_md
        assert 'subagent_type: "researcher"' in claude_md


class TestPart5MCP:
    """Verifies Feature 2: MCP Server (`mcp_server.py` and `.mcp.json`)."""

    def test_part_5a_mcp_tool_verify_hyperparameters(self) -> None:
        """Verify `@mcp.tool` `verify_hyperparameters` validates hyperparameter ranges."""
        output = verify_hyperparameters(
            living_reward=-0.04,
            discount_gamma=0.90,
            learning_rate_alpha=0.10,
            exploration_epsilon=0.20,
        )
        assert isinstance(output, str) and len(output.strip()) > 0
        with pytest.raises(ValueError):
            verify_hyperparameters(
                living_reward=1.0,
                discount_gamma=0.90,
                learning_rate_alpha=0.10,
                exploration_epsilon=0.20,
            )

    def test_part_5b_mcp_resource_hyperparameters(self) -> None:
        """Verify `@mcp.resource` `vacuum://hyperparameters` returns hyperparameter dict."""
        data = get_hyperparameters_resource()
        assert isinstance(data, dict)
        expected_keys = (
            "living_reward",
            "discount_gamma",
            "learning_rate_alpha",
            "exploration_epsilon",
        )
        for key in expected_keys:
            assert key in data
            assert data[key] is not None

    def test_part_5c_mcp_prompt_audit_hyperparameters(self) -> None:
        """Verify `@mcp.prompt` `audit_hyperparameters` returns instruction string."""
        prompt_text = audit_hyperparameters_prompt(living_reward="-0.04")
        assert isinstance(prompt_text, str) and len(prompt_text.strip()) > 20
        assert "verify_hyperparameters" in prompt_text
