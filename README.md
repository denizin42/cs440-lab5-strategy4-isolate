# CS 440 Lab 5 — Repository 2: Strategy 4 (Isolate) & Model-Free Tabular Q-Learning

**Group 2 Members:** David Jablonski (`@denizin42`), Chris Mills (`@chris-mills03`), James Richardson (`@RichardsonJC`)  
**Course:** CS 440 — Introduction to Artificial Intelligence (Fall 2026)  
**Companion Repository (Strategy 1: Write):** [`denizin42/cs440-lab5-strategy1-write`](https://github.com/denizin42/cs440-lab5-strategy1-write)

---

## 1. Purpose of Repository 2: Context Engineering Strategy 4 (Isolate)

In the **Agentic AI & Context Engineering** lecture (Slides 33–34), **Strategy 4: Isolate** prevents **Context Confusion** and **Context Poisoning** by splitting complex work across specialized sub-agents and process boundaries rather than crowding a single monolithic context window.

### How This Repository Contrasts with Repository 1 (`strategy1-write`)
| Architectural Layer | **Repo 2: `cs440-lab5-strategy4-isolate` (This Repo)** | **Repo 1: `cs440-lab5-strategy1-write`** |
| :--- | :--- | :--- |
| **Primary Context Strategy** | **Strategy 4: Isolate (Slides 33–34)** — Splitting work across an Orchestrator, a Context Filter, and isolated sub-agents/processes to prevent Context Confusion. | **Strategy 1: Write (Slides 21–28)** — Externalizing persistent memory, dynamic `@./context/*.md` imports, and procedural skills to disk. |
| **Primary `CLAUDE.md` Role** | **Main Agent Orchestrator** decomposing work via `Task(description, prompt, subagent_type)` through a strict Context Filter. | **3-Tier Persistent Memory** (`./CLAUDE.md`, `examples/user-memory-CLAUDE.md`, and `@./context/*.md` dynamic imports). |
| **Primary Sub-Agent & MCP Focus** | **Scoped Sub-Agents (`code-reviewer`, `researcher`)** + **Process-Isolated MCP `@mcp.tool`** running 8,000 Q-learning episodes in a separate subprocess outside the LLM context window. | **On-Demand Skills (`SKILL.md`)** + **MCP `@mcp.resource` & `@mcp.prompt`** to inject persisted hyperparameters and expert prompt templates. |
| **Primary Hook Focus** | **`PreToolUse` $\rightarrow$ `scripts/prevent-main-commit.sh`**: Enforces an execution boundary blocking direct agent commits to `main`. | **`UserPromptSubmit` $\rightarrow$ `scripts/context-switcher.sh`**: Dynamically writes `@./context/*.md` imports based on Git branch and query keywords using a `grep -qxF` duplicate guard. |

*(Note: Both repositories include all 4 Claude Code features—**Hooks, MCP, Skills, and Sub-agents**—and the complete 4x4 Vacuum Q-Learning solution so either repository can be graded standalone.)*

---

## 2. Four Layers of Isolation in This Repository

1. **Sub-Agent Context Isolation (`.claude/agents/code-reviewer.md` & `researcher.md` — Slides 33–34)**:
   - **`code-reviewer`**: Configured with YAML frontmatter (`tools: ["Read", "Grep", "Glob"]`, `model: sonnet`). Receives **ONLY** `git diff` and security/encapsulation rules to verify that `TabularQLearningAgent` never accesses private environment tables.
   - **`researcher`**: Configured with YAML frontmatter (`tools: ["Read", "Grep"]`, `model: sonnet`). Receives **ONLY** broad architectural queries comparing $\epsilon$-greedy vs. optimistic exploration $f(u, n) = u + k/n$.
2. **Process-Isolated Tool Execution via MCP (`.mcp.json` + `mcp_server.py` — MCP Lecture Slides 4–19)**:
   - Runs 8,000 episodes of stochastic Q-learning inside an isolated Python `FastMCP` subprocess over `stdio` (`@mcp.tool` `run_q_learning_experiment`) so thousands of intermediate step transitions never flood Claude's context window.
3. **Environment State Encapsulation (`src/environment.py` vs. `src/agent.py`)**:
   - Enforces the Model-Free RL boundary: `VacuumGridEnv` hides `_transition_weights` (`0.8 / 0.1 / 0.1`) and `_compute_reward()` behind a black-box `step(action) -> StepOutcome(state, action, next_state, reward, done)` contract, audited by `.claude/skills/q-learning-audit/SKILL.md`.
4. **Git Branch Isolation (`.githooks/pre-commit` + `scripts/prevent-main-commit.sh`)**:
   - Isolates the `main` branch from direct commits by both human developers (`pre-commit`) and AI agents (`PreToolUse` hook).

---

## 3. Selected Hyperparameters & Justification

| Hyperparameter | Variable | Selected Value | Justification |
| :--- | :--- | :---: | :--- |
| **Living Reward** | `living_reward` | **`-0.04`** | Matches the Lab 3 baseline living cost; penalizes extra steps enough to encourage the shortest safe path without making the robot reckless near the `-1.0` Trap at `(3, 1)`. |
| **Discount Factor** | `discount_gamma` | **`0.90`** | Ensures the `+10.0` terminal reward at `(3, 3)` propagates back across the 6-step path to `(0, 0)` and allows direct comparison against Lab 3 Value Iteration utilities. |
| **Learning Rate** | `learning_rate_alpha` | **`0.10`** | Smoothly averages Temporal-Difference samples over the `80% / 10% / 10%` stochastic slip transitions without oscillating after occasional slips. |
| **Exploration Rate** | `exploration_epsilon` | **`0.20`** | Guarantees 20% uniform random exploration during training so all 13 non-terminal states and 4 actions are thoroughly visited before extracting the greedy policy. |

---

## 4. Repository Structure

```text
cs440-lab5-strategy4-isolate/
├── README.md                                  # Strategy 4 (Isolate) documentation, comparison table, & CLI guide
├── KANBAN_BOARD.md                            # Combined Group 2 Kanban board
├── TEAM_ONBOARDING.md                         # Teammate clone & multi-agent setup instructions
├── CLAUDE.md                                  # [Strategy 4] Main Orchestrator Task() delegation & Context Filter rules
├── .mcp.json                                  # [Feature 2: MCP] Registers process-isolated FastMCP stdio server
├── mcp_server.py                              # [Feature 2: MCP] @mcp.tool, @mcp.resource, & @mcp.prompt server
├── .githooks/
│   └── pre-commit                             # Git pre-commit hook isolating `main` from direct commits
├── .claude/
│   ├── agents/                                # [Strategy 4 / Feature 4: Sub-Agents] YAML-scoped isolated sub-agents
│   │   ├── code-reviewer.md                   # Focused context: receives ONLY code diffs & encapsulation rules
│   │   └── researcher.md                      # Broad context: receives ONLY RL & exploration math queries
│   ├── settings.json                          # [Feature 1: Hooks] PreToolUse (branch isolation) + UserPromptSubmit
│   ├── skills/                                # [Feature 3: Skills] On-demand procedural skills
│   │   ├── q-learning-audit/
│   │   │   └── SKILL.md                       # Audits T/R encapsulation between VacuumGridEnv and Agent
│   │   └── github-kanban-sync/
│   │       ├── SKILL.md
│   │       └── scripts/sync-kanban.sh
│   └── context/                               # Modular domain context files
├── context/                                   # Dynamic @./context/*.md files
├── examples/
│   └── user-memory-CLAUDE.md                  # Reference example for ~/.claude/CLAUDE.md
├── scripts/
│   ├── prevent-main-commit.sh                 # [Strategy 4] PreToolUse guard isolating `main` from direct commits
│   ├── context-switcher.sh                    # Branch + prompt context switcher with grep -qxF guard
│   └── setup-teammate.sh                      # Multi-agent onboarding script (Claude, Cursor, Copilot, Gemini)
├── src/
│   ├── __init__.py
│   ├── environment.py                         # Black-box 4x4 VacuumGridEnv simulator (isolates hidden T and R)
│   ├── agent.py                               # Hyperparameters & TabularQLearningAgent (TD update + exploration)
│   └── q_learning.py                          # CLI runner printing utilities, Q-table, policy, and rollout logs
└── tests/
    └── test_lab5_progress.py                  # Automated 14-test pytest suite verifying all Lab 5 requirements
```

---

## 5. How to Run the Solution & Tests

```bash
# 1. One-time teammate & pre-commit hook setup:
bash scripts/setup-teammate.sh --agent all

# 2. Run the 14-test verification suite:
pytest -v

# 3. Run the Q-Learning training, policy extraction, and stochastic rollout demo:
python3 -m src.q_learning
```
