# CS 440 Lab 5 — Group 2 Repository Update & Quick Setup Guide

Hey team (`@Chris Mills`, `@James Richardson`) — I've updated our **Lab 5** GitHub setup now that we have the full picture of how **Lab 4** (Context Engineering Strategies 1 & 4) and **Lab 5** (Solving the 4x4 Vacuum Q-Learning problem + using the Claude Code features) fit together.

---

## 1. Updated GitHub Repositories (Old Single Repo Archived)

- **Archived (No Longer Used):** `https://github.com/denizin42/cs440-lab4-strategy1-4`
- **Active Repo 1 — Strategy 1 (Write) + All 4 Features:**  
  [`https://github.com/denizin42/cs440-lab5-strategy1-write`](https://github.com/denizin42/cs440-lab5-strategy1-write)
- **Active Repo 2 — Strategy 4 (Isolate) + All 4 Features:**  
  [`https://github.com/denizin42/cs440-lab5-strategy4-isolate`](https://github.com/denizin42/cs440-lab5-strategy4-isolate)

*(Both of you have collaborator push access on both repositories—check your GitHub notifications/email if you haven't accepted the invite yet!)*

---

## 2. Fast Clone & Setup (With Your Preferred AI Coding Agent)

Each repository includes `scripts/setup-teammate.sh`, which automatically:
1. Activates our versioned **Git `pre-commit` hook** (`.githooks/pre-commit`) so nobody accidentally commits directly to `main`.
2. Bridges `CLAUDE.md` and `.mcp.json` to your preferred coding agent (**Claude Code**, **Cursor**, **GitHub Copilot / VS Code**, or **Gemini / Antigravity / Codex**) using `.git/info/exclude` so agent-specific symlinks never dirty `git status`.
3. Verifies your `python3` + `pytest` setup and updates [`KANBAN_BOARD.md`](./KANBAN_BOARD.md).

### Clone Both Repos & Configure Your Agent in One Command:
```bash
# Clone both Group 2 repositories:
git clone https://github.com/denizin42/cs440-lab5-strategy1-write.git
git clone https://github.com/denizin42/cs440-lab5-strategy4-isolate.git

# Inside either repo, run the setup script with your preferred agent
# Options for --agent: claude | cursor | copilot | gemini | all (default: all)
cd cs440-lab5-strategy1-write
bash scripts/setup-teammate.sh --agent all --branch feature/q-learning
```

---

## 3. Repository Structure & What's Inside

```text
cs440-lab5-strategy1-write/  (and cs440-lab5-strategy4-isolate/)
├── README.md                                  # Full project overview, hyperparameter table, & CLI docs
├── KANBAN_BOARD.md                            # Combined Group 2 Kanban board (auto-updated via skill!)
├── CLAUDE.md                                  # Project Memory, Orchestrator Task() rules, & @./context imports
├── .mcp.json                                  # [Feature 2: MCP] Local stdio FastMCP server config
├── mcp_server.py                              # [Feature 2: MCP] @mcp.tool, @mcp.resource, & @mcp.prompt server
├── .githooks/
│   └── pre-commit                             # Blocks direct git commits to `main` (enforces feature/* branches)
├── .claude/
│   ├── settings.json                          # [Feature 1: Hooks] PreToolUse (no main commit) + UserPromptSubmit
│   ├── context/                               # Modular context files echoed by context-switcher.sh
│   │   ├── environment.md
│   │   ├── q-learning.md
│   │   └── exploration.md
│   ├── skills/
│   │   ├── github-kanban-sync/                # [Feature 3: Skills] Working skill that syncs KANBAN_BOARD.md & GitHub Issues
│   │   │   ├── SKILL.md
│   │   │   └── scripts/sync-kanban.sh
│   │   └── q-learning-audit/
│   │       └── SKILL.md                       # [Feature 3: Skills] On-demand Bellman & T/R encapsulation audit skill
│   └── agents/                                # [Feature 4: Sub-Agents] YAML-configured isolated sub-agents
│       ├── code-reviewer.md                   # Focused context: receives ONLY code diffs & encapsulation rules
│       └── researcher.md                      # Broad context: receives ONLY RL & exploration math queries
├── context/                                   # Dynamic @./context/*.md imports referenced by CLAUDE.md
├── scripts/
│   ├── context-switcher.sh                    # [Feature 1: Hooks] Branch + prompt selector with grep -qxF guard
│   ├── prevent-main-commit.sh                 # [Feature 1: Hooks] Claude PreToolUse guard blocking commits on main
│   └── setup-teammate.sh                      # One-command onboarding & multi-agent setup script
├── src/
│   ├── environment.py                         # Complete black-box 4x4 VacuumGridEnv simulator (encapsulates T & R)
│   ├── agent.py                               # Hyperparameters & TabularQLearningAgent (guided TODOs in Part 1)
│   └── q_learning.py                          # CLI runner printing utilities, Q-table, policy, & rollout logs
└── tests/
    └── test_lab5_progress.py                  # Interactive 14-test pytest suite verifying Parts 1 through 5
```

---

## 4. Group 2 Kanban Task Breakdown (`KANBAN_BOARD.md`)

All tasks are tracked in [`KANBAN_BOARD.md`](./KANBAN_BOARD.md) and verified by `pytest -v`:

| Card | Task / Scope | Files to Edit | Suggested Owner | Test Command |
| :---: | :--- | :--- | :--- | :--- |
| **#1** | **Part 1:** Q-Learning Hyperparameters (`living_reward=-0.04, gamma=0.90, alpha=0.10, epsilon=0.20`), $\epsilon$-greedy `select_action()`, and Bellman TD `update()` | `src/agent.py` | `@RichardsonJC` / `@denizin42` | `pytest -v -k TestPart1QLearning` |
| **#2** | **Part 2 (Hooks & Memory):** Register `UserPromptSubmit` hook, `grep -qxF` guard, & uncomment `@./context/*.md` | `.claude/settings.json`, `scripts/context-switcher.sh`, `CLAUDE.md` | `@chris-mills03` | `pytest -v -k TestPart2HooksAndMemory` |
| **#3** | **Part 3 (Skills):** Complete `q-learning-audit` YAML frontmatter (using `github-kanban-sync/SKILL.md` as reference) | `.claude/skills/q-learning-audit/SKILL.md` | `@chris-mills03` | `pytest -v -k TestPart3Skills` |
| **#4** | **Part 4 (Sub-Agents):** Complete YAML frontmatter in `code-reviewer.md` & `researcher.md`, and `Task()` in `CLAUDE.md` | `.claude/agents/*.md`, `CLAUDE.md` | `@RichardsonJC` | `pytest -v -k TestPart4SubAgents` |
| **#5** | **Part 5 (MCP):** Complete `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt` in `mcp_server.py` | `mcp_server.py` | `@denizin42` | `pytest -v -k TestPart5MCP` |
| **#6** | **Part 6 (Final Sync & Video):** Sync both repos, verify all 14 tests pass, and record 3-min video | `VIDEO_PRESENTATION_GUIDE.md` | All 3 Members | `pytest -v && python3 -m src.q_learning` |

---

## 5. Branch Workflow Reminder (Pre-Commit Hook Active!)

Direct commits to `main` are blocked by `.githooks/pre-commit` and `.claude/settings.json`. Always work on a feature branch:
```bash
git checkout -b feature/q-learning      # or feature/environment, feature/exploration
pytest -v                               # verify your part passes
bash .claude/skills/github-kanban-sync/scripts/sync-kanban.sh --update-board
git add . && git commit -m "Complete Part X"
git push -u origin HEAD
```
