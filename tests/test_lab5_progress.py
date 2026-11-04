"""CS 440 Lab 5 Progress & Verification Test Suite.

Run all checks:
    pytest -v

Or test individual parts as you complete each TODO:
    pytest -v -k TestPart1QLearning
    pytest -v -k TestPart2HooksAndMemory
    pytest -v -k TestPart3Skills
    pytest -v -k TestPart4SubAgents
    pytest -v -k TestPart5MCP
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mcp_server import (
    audit_hyperparameters_prompt,
    get_hyperparameters_resource,
    list_context_docs,
    read_context_doc,
    run_q_learning_experiment,
)
from src.agent import Hyperparameters, TabularQLearningAgent
from src.environment import VALID_ACTIONS, VacuumGridEnv
from src.q_learning import evaluate_policy_reliability, run_experiment


class TestPart1QLearning:
    """Verifies Part 1A (Hyperparameters), Part 1B (select_action), and Part 1C (update)."""

    def test_part_1a_hyperparameters_selected(self) -> None:
        """Verify all 4 hyperparameters in `Hyperparameters` are set to valid numbers."""
        params = Hyperparameters()
        assert params.living_reward is not None, "TODO Part 1A: Set living_reward in Hyperparameters"
        assert params.discount_gamma is not None, "TODO Part 1A: Set discount_gamma in Hyperparameters"
        assert params.learning_rate_alpha is not None, "TODO Part 1A: Set learning_rate_alpha in Hyperparameters"
        assert params.exploration_epsilon is not None, "TODO Part 1A: Set exploration_epsilon in Hyperparameters"

        assert params.living_reward < 0.0, "living_reward should be negative (e.g., -0.04)"
        assert 0.0 < params.discount_gamma <= 1.0, "discount_gamma must be in (0, 1]"
        assert 0.0 < params.learning_rate_alpha <= 1.0, "learning_rate_alpha must be in (0, 1]"
        assert 0.0 <= params.exploration_epsilon <= 1.0, "exploration_epsilon must be in [0, 1]"

    def test_part_1b_epsilon_greedy_action_selection(self) -> None:
        """Verify `select_action()` explores with probability epsilon and exploits otherwise."""
        params = Hyperparameters(
            living_reward=-0.04,
            discount_gamma=0.90,
            learning_rate_alpha=0.10,
            exploration_epsilon=0.0,
            seed=42,
        )
        agent = TabularQLearningAgent(params)
        agent._ensure_state_initialized((0, 0))
        agent._q_table[(0, 0)]["Right"] = 5.0

        # When epsilon=0.0, must deterministically pick the highest-Q action ("Right")
        for _ in range(10):
            assert agent.select_action((0, 0), training=True) == "Right"

        # When epsilon=1.0, must explore multiple actions over 40 draws
        explore_agent = TabularQLearningAgent(
            Hyperparameters(
                living_reward=-0.04,
                discount_gamma=0.90,
                learning_rate_alpha=0.10,
                exploration_epsilon=1.0,
                seed=42,
            )
        )
        sampled_actions = {explore_agent.select_action((0, 0), training=True) for _ in range(40)}
        assert len(sampled_actions) > 1

    def test_part_1c_bellman_td_update_and_terminal_boundary(self) -> None:
        """Verify `update()` applies Q(s,a) <- (1-alpha)Q(s,a) + alpha*(r + gamma*max_a' Q(s',a'))."""
        params = Hyperparameters(
            living_reward=-0.04,
            discount_gamma=0.90,
            learning_rate_alpha=0.10,
            exploration_epsilon=0.20,
            seed=42,
        )
        agent = TabularQLearningAgent(params)

        # Terminal transition into Recharge Goal (3, 3) with reward +10.0 (`done=True`)
        td_error = agent.update(
            state=(2, 3),
            action="Down",
            reward=10.0,
            next_state=(3, 3),
            done=True,
        )
        assert pytest.approx(td_error, abs=1e-6) == 10.0
        assert pytest.approx(agent.get_q_value((2, 3), "Down"), abs=1e-6) == 1.0
        assert agent.visit_counts[(2, 3)]["Down"] == 1

        # Non-terminal transition into (2, 3) where max_a' Q((2, 3), a') == 1.0
        # sample = -0.04 + 0.90 * 1.0 = 0.86 -> updated Q = 0.10 * 0.86 = 0.086
        agent.update(
            state=(1, 3),
            action="Down",
            reward=-0.04,
            next_state=(2, 3),
            done=False,
        )
        assert pytest.approx(agent.get_q_value((1, 3), "Down"), abs=1e-6) == 0.086

    def test_full_q_learning_convergence_to_optimal_policy(self) -> None:
        """Verify trained agent avoids Trap (3, 1) and reaches Recharge Goal (3, 3)."""
        params = Hyperparameters()
        env, agent = run_experiment(params)
        policy = agent.extract_policy(env)

        # At (3, 0), immediately left of Trap (3, 1), optimal policy must NOT move Right into the trap
        assert policy[(3, 0)] != "Right"
        # Adjacent to Recharge Goal (3, 3): (2, 3) must move Down and (3, 2) must move Right
        assert policy[(2, 3)] == "Down"
        assert policy[(3, 2)] == "Right"

        metrics = evaluate_policy_reliability(policy, living_reward=params.living_reward)
        assert metrics["recharge_rate_pct"] >= 95.0
        assert metrics["trap_rate_pct"] == 0.0


class TestPart2HooksAndMemory:
    """Verifies Feature 1: Hooks (.claude/settings.json, scripts/context-switcher.sh, CLAUDE.md)."""

    def test_pre_commit_hook_blocks_main_branch(self) -> None:
        """Verify `.githooks/pre-commit` and Claude `PreToolUse` hook block direct commits to `main`."""
        git_hook = REPO_ROOT / ".githooks" / "pre-commit"
        claude_pre_hook = REPO_ROOT / "scripts" / "prevent-main-commit.sh"
        settings_path = REPO_ROOT / ".claude" / "settings.json"

        assert git_hook.exists(), ".githooks/pre-commit must exist"
        assert claude_pre_hook.exists(), "scripts/prevent-main-commit.sh must exist"
        assert "Direct commits to" in git_hook.read_text(encoding="utf-8")

        data = json.loads(settings_path.read_text(encoding="utf-8"))
        pre_tool_cmd = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert "scripts/prevent-main-commit.sh" in pre_tool_cmd

    def test_part_2a_settings_json_hook_registered(self) -> None:
        """Verify `.claude/settings.json` registers `scripts/context-switcher.sh` under `UserPromptSubmit`."""
        settings_path = REPO_ROOT / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        command = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        assert "TODO" not in command, "TODO Part 2A: Set the hook command in .claude/settings.json"
        assert "scripts/context-switcher.sh" in command

    def test_part_2b_context_switcher_idempotency_guard(self, tmp_path: Path) -> None:
        """Verify `scripts/context-switcher.sh` uses `grep -qxF` and never duplicates imports."""
        script_path = REPO_ROOT / "scripts" / "context-switcher.sh"
        script_text = script_path.read_text(encoding="utf-8")
        assert "grep -qxF" in script_text, "TODO Part 2B: Use grep -qxF inside add_context()"
        assert "return 1" not in script_text, "TODO Part 2B: Remove placeholder `return 1` in add_context()"

    def test_part_2c_claude_md_dynamic_context_imports(self) -> None:
        """Verify `CLAUDE.md` contains uncommented `@./context/*.md` imports at the root column."""
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        active_lines = [
            line
            for line in claude_md.splitlines()
            if line.startswith("@./context/")
        ]
        assert "@./context/environment.md" in active_lines, "TODO Part 2C: Add @./context/environment.md at start of line in CLAUDE.md"
        assert "@./context/q-learning.md" in active_lines, "TODO Part 2C: Add @./context/q-learning.md at start of line in CLAUDE.md"
        assert "@./context/exploration.md" in active_lines, "TODO Part 2C: Add @./context/exploration.md at start of line in CLAUDE.md"


class TestPart3Skills:
    """Verifies Feature 3: On-Demand Claude Code Skill (`.claude/skills/q-learning-audit/SKILL.md`)."""

    def test_part_3_skill_frontmatter(self) -> None:
        """Verify `.claude/skills/q-learning-audit/SKILL.md` defines valid `name` and `description`."""
        skill_text = (
            REPO_ROOT / ".claude" / "skills" / "q-learning-audit" / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert "TODO_PART_3" not in skill_text, "TODO Part 3: Fill in name and description in SKILL.md"
        assert "name: q-learning-audit" in skill_text


class TestPart4SubAgents:
    """Verifies Feature 4: Isolated Sub-Agents (`.claude/agents/*.md` and `CLAUDE.md` Task() rules)."""

    def test_part_4a_subagent_yaml_frontmatter(self) -> None:
        """Verify `code-reviewer.md` and `researcher.md` have complete YAML frontmatter."""
        reviewer_text = (REPO_ROOT / ".claude" / "agents" / "code-reviewer.md").read_text(encoding="utf-8")
        researcher_text = (REPO_ROOT / ".claude" / "agents" / "researcher.md").read_text(encoding="utf-8")

        assert "TODO_PART_4A" not in reviewer_text, "TODO Part 4A: Complete frontmatter in code-reviewer.md"
        assert "name: code-reviewer" in reviewer_text
        assert '"Read"' in reviewer_text and '"Grep"' in reviewer_text

        assert "TODO_PART_4A" not in researcher_text, "TODO Part 4A: Complete frontmatter in researcher.md"
        assert "name: researcher" in researcher_text
        assert '"Read"' in researcher_text and '"Grep"' in researcher_text

    def test_part_4b_claude_md_task_delegation(self) -> None:
        """Verify `CLAUDE.md` delegates to `code-reviewer` and `researcher` via `Task()`."""
        claude_md = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "TODO_SET_REVIEWER_SUBAGENT" not in claude_md, "TODO Part 4B: Set code-reviewer in CLAUDE.md"
        assert "TODO_SET_RESEARCHER_SUBAGENT" not in claude_md, "TODO Part 4B: Set researcher in CLAUDE.md"
        assert 'subagent_type: "code-reviewer"' in claude_md
        assert 'subagent_type: "researcher"' in claude_md


class TestPart5MCP:
    """Verifies Feature 2: MCP Server (`mcp_server.py` and `.mcp.json`)."""

    def test_part_5a_mcp_tool_run_q_learning_experiment(self) -> None:
        """Verify `@mcp.tool` `run_q_learning_experiment` executes and returns grid output."""
        output = run_q_learning_experiment(
            living_reward=-0.04,
            discount_gamma=0.90,
            learning_rate_alpha=0.10,
            exploration_epsilon=0.20,
            num_episodes=1000,
        )
        assert "Learned State Utilities" in output
        assert "Learned Greedy Policy" in output

    def test_part_5b_mcp_resource_hyperparameters(self) -> None:
        """Verify `@mcp.resource` `vacuum://hyperparameters` returns selected hyperparameter dict."""
        data = get_hyperparameters_resource()
        assert isinstance(data, dict)
        for key in ("living_reward", "discount_gamma", "learning_rate_alpha", "exploration_epsilon"):
            assert key in data
            assert data[key] is not None

    def test_part_5c_mcp_prompt_audit_hyperparameters(self) -> None:
        """Verify `@mcp.prompt` `audit_hyperparameters` returns a non-empty instruction string."""
        prompt_text = audit_hyperparameters_prompt(living_reward="-0.04")
        assert isinstance(prompt_text, str) and len(prompt_text.strip()) > 20
        assert "run_q_learning_experiment" in prompt_text
