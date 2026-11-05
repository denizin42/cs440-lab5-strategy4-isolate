# Target Output Directory for the AI Agent (`src/`)

This directory intentionally starts **without any pre-written Python code**.

## Workflow
1. **Human Setup (Context Engineering):**
   Complete the `TODO` sections in the repository's Context Engineering markdown and configuration files (`CLAUDE.md`, `.claude/settings.json`, `scripts/context-switcher.sh`, `.claude/skills/q-learning-audit/SKILL.md`, `.claude/agents/*.md`, and `mcp_server.py`).
2. **Verify Context Engineering Setup:**
   Run `pytest -v` to confirm all Context Engineering rules, hooks, skills, sub-agents, MCP primitives, and hyperparameter specifications in `CLAUDE.md` are valid.
3. **Run the Agent (`agy` / `claude`) to Generate the Solution:**
   Instruct your coding agent to read `CLAUDE.md` and generate the complete 4x4 Vacuum Robot Tabular Q-Learning solution inside `src/` using the configured Hooks, MCP server, Skills, and Sub-agents.
