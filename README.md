# CS 440 Lab 5: Strategy 4 (Isolate) — 4x4 Vacuum Robot Q-Learning & All 4 Claude Code Features

**Group 2 Members:** David Jablonski (`@denizin42`), Chris Mills (`@chris-mills03`), James Richardson (`@RichardsonJC`)  
**Course:** CS 440 — Introduction to Artificial Intelligence (Fall 2026)

---

## 1. Overview & Problem Specification

In **Lab 4**, we scaffolded our Context Engineering repository for the **4x4 Vacuum Robot** where the transition model $T(s, a, s')$ and reward function $R(s, a, s')$ are **unknown**. In **Lab 5**, we solve this environment using **Model-Free Tabular Q-Learning** while integrating **all 4 Claude Code features** (**Hooks**, **MCP**, **Skills**, and **Sub-agents**).

```text
Row \ Col    0        1        2        3
   0      [start]  [  0  ]  [  0  ]  [  0  ]
   1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
   2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
   3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
```

- **Start State `(0, 0)`**: Top-left corner (`0`).
- **Obstacle `X` at `(1, 1)`**: Impassable pillar; bumping into `(1, 1)` or an outer wall leaves the robot in place.
- **Terminal Trap `-1` at `(3, 1)`**: Hazard yielding `-1.0` and ending the episode.
- **Terminal Recharge Goal `+10` at `(3, 3)`**: Recharge station yielding `+10.0` and ending the episode.
- **Stochastic Slip Dynamics (Hidden from Agent)**: Intended direction occurs with probability `0.80`, slipping $90^\circ$ left with `0.10`, and slipping $90^\circ$ right with `0.10`.

---

## 2. Project Structure

```text
cs440-lab5-strategy4-isolate/
├── README.md                                  # Project documentation, hyperparameters, and run instructions
├── CLAUDE.md                                  # Project Memory, Orchestrator Task() rules, and @./context imports
├── .mcp.json                                  # [Feature 2: MCP] Registers local FastMCP stdio server
├── mcp_server.py                              # [Feature 2: MCP] @mcp.tool, @mcp.resource, and @mcp.prompt server
├── .claude/
│   ├── settings.json                          # [Feature 1: Hooks] Registers UserPromptSubmit -> context-switcher.sh
│   ├── context/                               # Modular domain context echoed by context-switcher.sh
│   │   ├── environment.md
│   │   ├── q-learning.md
│   │   └── exploration.md
│   ├── skills/
│   │   └── q-learning-audit/
│   │       └── SKILL.md                       # [Feature 3: Skills] On-demand Bellman & encapsulation audit skill
│   └── agents/                                # [Feature 4: Sub-Agents] YAML-configured isolated sub-agents
│       ├── code-reviewer.md                   # Focused context: receives ONLY code diffs & encapsulation rules
│       └── researcher.md                      # Broad context: receives ONLY RL & exploration math queries
├── context/                                   # Dynamic @./context/*.md imports referenced by CLAUDE.md
│   ├── environment.md
│   ├── q-learning.md
│   └── exploration.md
├── examples/
│   └── user-memory-CLAUDE.md                  # Reference example for ~/.claude/CLAUDE.md
├── scripts/
│   └── context-switcher.sh                    # [Feature 1: Hooks] Branch + prompt selector with grep -qxF guard
├── src/
│   ├── __init__.py
│   ├── environment.py                         # Black-box 4x4 VacuumGridEnv simulator (encapsulates T and R)
│   ├── agent.py                               # Hyperparameters & TabularQLearningAgent (TD update + exploration)
│   └── q_learning.py                          # CLI runner printing utilities, Q-table, policy, and rollout logs
└── tests/
    └── test_lab5_progress.py                  # Automated pytest suite verifying all 5 parts of Lab 5
```

---

## 3. Selected Hyperparameters & Justification

| Hyperparameter | Variable | Selected Value | Justification |
| :--- | :--- | :---: | :--- |
| **Living Reward** | `living_reward` | **`-0.04`** | Matches the Lab 3 baseline living cost; penalizes extra steps enough to encourage the shortest safe path without making the robot reckless near the `-1.0` Trap at `(3, 1)`. |
| **Discount Factor** | `discount_gamma` | **`0.90`** | Ensures the `+10.0` terminal reward at `(3, 3)` propagates back across the 6-step path to `(0, 0)` and allows direct comparison against Lab 3 Value Iteration utilities. |
| **Learning Rate** | `learning_rate_alpha` | **`0.10`** | Smoothly averages Temporal-Difference samples over the `80% / 10% / 10%` stochastic slip transitions without oscillating after occasional slips. |
| **Exploration Rate** | `exploration_epsilon` | **`0.20`** | Guarantees 20% uniform random exploration during training so all 13 non-terminal states and 4 actions are thoroughly visited before extracting the greedy policy. |

---

## 4. How All 4 Claude Code Features Are Used

1. **Hooks (`.claude/settings.json` + `scripts/context-switcher.sh`)**:
   - Registers a `UserPromptSubmit` hook that inspects the active Git branch (`feature/environment*`, `feature/q-learning*`, `feature/exploration*`) and prompt keywords, dynamically injecting relevant context while guarding against duplicate `@./context/*.md` imports in `CLAUDE.md` via `grep -qxF`.
2. **MCP (`.mcp.json` + `mcp_server.py`)**:
   - Implements a `FastMCP` server (`VacuumRLMCP`) exposing all three MCP primitives from lecture:
     - **Tools (`@mcp.tool`)**: `run_q_learning_experiment` and `read_context_doc`.
     - **Resources (`@mcp.resource`)**: `vacuum://hyperparameters` and `vacuum://context`.
     - **Prompts (`@mcp.prompt`)**: `/audit_hyperparameters` reusable verification template.
3. **Skills (`.claude/skills/q-learning-audit/SKILL.md`)**:
   - Provides an on-demand procedural checklist verifying model-free $T$/$R$ encapsulation, terminal state value boundary ($\max_{a'} Q(s_{\text{terminal}}, a') = 0.0$), and random tie-breaking.
4. **Sub-Agents (`.claude/agents/code-reviewer.md` & `.claude/agents/researcher.md`)**:
   - Isolates context using YAML frontmatter (`name`, `description`, `tools`, `model`) and orchestrator `Task()` delegation in `CLAUDE.md` so code review diffs and broad RL math queries never pollute a single monolithic context window.

---

## 5. How to Run the Solution & Tests

### Run the Interactive Progress & Unit Test Suite
```bash
pytest -v
```

### Run the Q-Learning Training, Policy Extraction, and Stochastic Simulation
```bash
python3 -m src.q_learning
```

### Run with Custom Hyperparameter Flags
```bash
python3 -m src.q_learning --living-reward -0.04 --gamma 0.90 --alpha 0.10 --epsilon 0.20 --episodes 8000
```
