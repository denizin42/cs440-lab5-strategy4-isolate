# Project Context: CS 440 Lab 5 — Strategy 4: Isolate (Orchestrator, Context Filter & Scoped Sub-Agents)

## 1. Strategy 4 (Isolate) Architecture Overview (Lecture Slides 33–34)
This repository (`cs440-lab5-strategy4-isolate`) focuses on **Context Engineering Strategy 4: Isolate**—partitioning work across an **Orchestrator**, a **Context Filter**, **YAML-scoped Sub-Agents**, and a **process-isolated MCP Server** so that debugging logs, code review diffs, and reinforcement learning math never collide in a single monolithic context window (**Context Confusion** / **Context Poisoning**).

```text
+-----------------------------------------------------------------------+
|                     Main Claude Agent (Orchestrator)                  |
|                 Decomposes tasks via Task(...) in CLAUDE.md           |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
                     +--------------+--------------+
                     |       Context Filter        |
                     |  Strips full chat history;  |
                     |  passes ONLY scoped payload |
                     +------+---------------+------+
                            |               |
          +-----------------+               +-----------------+
          | Scoped Diff Only                                  | Broad Math Query Only
          v                                                   v
+-----------------------------------+       +-----------------------------------+
| Sub-Agent: `code-reviewer`        |       | Sub-Agent: `researcher`           |
| (.claude/agents/code-reviewer.md) |       | (.claude/agents/researcher.md)    |
| Tools: ["Read", "Grep", "Glob"]   |       | Tools: ["Read", "Grep"]           |
| Audits T/R encapsulation & diffs  |       | Analyzes Bellman TD & Exploration |
+-----------------------------------+       +-----------------------------------+
```

---

## 2. Sub-Agent Delegation Rules (Strategy 4: Context Isolation — Slides 33–34)
You are the **Main Claude Agent (Orchestrator)**. Do not mix broad mathematical research, coding, and security/encapsulation code reviews in one conversation history. Delegate specialized tasks through the **Context Filter** to the isolated sub-agents defined in `.claude/agents/`:

1. **`code-reviewer` (`.claude/agents/code-reviewer.md`)**:
   - **Scoped Context**: Receives **ONLY** the code diff (`git diff`) and security/encapsulation rules; restricted to read-only tools `["Read", "Grep", "Glob"]`.
   - **Purpose**: Verify that the learning agent generated in `src/` never reads hidden $T(s,a,s')$ or $R(s,a,s')$ tables and that terminal state boundaries (`done=True`) are respected.
2. **`researcher` (`.claude/agents/researcher.md`)**:
   - **Scoped Context**: Receives **ONLY** broad architectural queries regarding Q-learning Bellman updates, convergence conditions, and $\epsilon$-greedy vs. optimistic exploration $f(u, n) = u + k/n$; restricted to `["Read", "Grep"]`.

```javascript

// Code review agent - focused context (Slide 34)
Task(
  description: "Code review",
  prompt: "Review this PR focusing only on security, performance, and model-free T/R encapsulation",
  subagent_type: "code-reviewer"
)

// Research agent - broad architectural query (Slide 34)
Task(
  description: "Research implementation",
  prompt: "Compare epsilon-greedy vs optimistic exploration f(u,n)=u+k/n for the 4x4 vacuum grid",
  subagent_type: "researcher"
)
```

---

## 3. Domain Isolation Boundary & Selected Hyperparameters
```text
Row \ Col    0        1        2        3
   0      [start]  [  0  ]  [  0  ]  [  0  ]
   1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
   2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
   3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
```
- **Strict Object Encapsulation**: When generating the Python solution in `src/`, the environment simulator must isolate private transition probabilities (`0.8` intended, `0.1` slip left, `0.1` slip right) and reward lookup (`+10.0` at `(3,3)`, `-1.0` at `(3,1)`, `living_reward` elsewhere) from the learning agent.
- **Branch Isolation (`PreToolUse` Hook)**: `.claude/settings.json` invokes `scripts/prevent-main-commit.sh` to isolate the `main` branch from direct agent commits.

### Selected Q-Learning Hyperparameters (Agent Must Use These Values When Generating `src/`)
| Hyperparameter | Variable Name | Selected Value |
| :--- | :--- | :--- |
| Living Reward | `living_reward` | `-0.04` |
| Discount Factor ($\gamma$) | `discount_gamma` | `0.90` |
| Learning Rate ($\alpha$) | `learning_rate_alpha` | `0.10` |
| Exploration Rate ($\epsilon$) | `exploration_epsilon` | `0.20` |

### Agent Implementation Instructions for `src/` (Autonomous Zero-Prompt Protocol)
**CRITICAL DIRECTIVE FOR THE AGENT**: Do **NOT** ask the user any clarifying questions or pause for confirmation. Execute the entire workflow below end-to-end autonomously in a single run:

1. **Branch Isolation (`PreToolUse` Hook Compliance)**:
   - Check the current branch (`git branch --show-current`). If on `main`, immediately create or switch to a feature branch: `git checkout -B feat/live-demo-q-learning`.
2. **MCP Hyperparameter Audit**:
   - Call `get_hyperparameters_resource()`, `verify_hyperparameters(-0.04, 0.90, 0.10, 0.20)`, and `audit_hyperparameters_prompt(-0.04)` from `mcp_server.py` and print the verification output.
3. **Generate Model-Free Q-Learning Implementation in `src/`**:
   - Create `src/__init__.py`, `src/environment.py` (`VacuumGridEnv` with private $T$ and $R$), `src/agent.py` (`QLearningHyperparameters` and `TabularQLearningAgent` supporting both `epsilon_greedy` and `optimistic` $f(u, n) = u + k/(n+1)$ with $k=2.0$), `src/q_learning.py`, and `tests/test_q_learning.py`.
   - Enforce PEP 484 type annotations, lines `<= 100` characters, module/class/function docstrings, zero future bootstrap (`0.0`) when `done=True`, and uniform random tie-breaking.
4. **Execute Full Learning Experiment, Hyperparameter Sensitivity Sweep & Publish Report**:
   - Run `python3 -m src.q_learning` to:
     - Train for **10,000 episodes** (`max_steps=100`, `seed=42`) and evaluate the greedy policy ($\epsilon = 0$) over **1,000 test episodes** for both `epsilon_greedy` and `optimistic` exploration modes using the baseline hyperparameters (`living_reward=-0.04, discount_gamma=0.90, learning_rate_alpha=0.10, exploration_epsilon=0.20`).
     - Run a **4-dimensional hyperparameter sensitivity sweep** (varying `living_reward` in `{-0.04, -0.50, -2.50}`, `discount_gamma` in `{0.50, 0.90, 0.99}`, `learning_rate_alpha` in `{0.01, 0.10, 0.80}`, and `exploration_epsilon` in `{0.05, 0.20, 0.50}`) validated by `verify_hyperparameters` in `mcp_server.py`.
   - Print the learned state utilities $V(s) = \max_a Q(s, a)$, greedy policy grid $\pi^*(s) = \arg\max_a Q(s, a)$, evaluation metrics, and hyperparameter sweep summary table to stdout, and write the complete report (including full $Q(s, a)$, visit count $N(s, a)$, and sensitivity sweep tables) to `EXPERIMENT_REPORT.md`.
5. **Delegate Sub-Agent Audits (Strategy 4: Isolate)**:
   - Invoke the isolated `code-reviewer` sub-agent to audit `src/` for model-free $T/R$ encapsulation, terminal state boundaries, and type safety.
   - Invoke the isolated `researcher` sub-agent to compare $\epsilon$-greedy vs. optimistic exploration $f(u, n)$ and include its summary in `EXPERIMENT_REPORT.md`.
6. **Verify Tests, Pylint (`10.00/10`), and Changelog**:
   - Run `python3 -m pytest -v` and `python3 -m pylint mcp_server.py tests/*.py src/*.py` (fixing any warnings until rated `10.00/10`).
   - Stage a Keep-a-Changelog entry via `bash scripts/changelog-add.sh Added "Implement 4x4 Vacuum World Q-Learning solution and EXPERIMENT_REPORT.md"` and commit on the feature branch.

---

## 4. Cross-Reference: Dynamic Context Imports (Supported Alongside Strategy 4)
<!--
TODO (Part 2C - Dynamic Context Imports, Slide 25):
Uncomment or add the three `@./context/*.md` lines below so Claude Code dynamically
loads the modular environment, Q-learning, and exploration context files:
-->
@./context/environment.md
@./context/q-learning.md
@./context/exploration.md
