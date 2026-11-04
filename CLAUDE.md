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
   - **Purpose**: Verify that `TabularQLearningAgent` never reads hidden $T(s,a,s')$ or $R(s,a,s')$ tables inside `VacuumGridEnv` and that terminal state boundaries (`done=True`) are respected.
2. **`researcher` (`.claude/agents/researcher.md`)**:
   - **Scoped Context**: Receives **ONLY** broad architectural queries regarding Q-learning Bellman updates, convergence conditions, and $\epsilon$-greedy vs. optimistic exploration $f(u, n) = u + k/n$; restricted to `["Read", "Grep"]`.
3. **Process-Isolated MCP Execution (`mcp_server.py` + `.mcp.json`)**:
   - Runs 8,000 stochastic Q-learning training episodes in an isolated subprocess over `stdio` via `@mcp.tool` (`run_q_learning_experiment`), returning only the converged 4x4 utilities and policy grid to the orchestrator.

```javascript
// ============================================================================
// TODO (Part 4B - Orchestrator Task Delegation, Slide 34):
// Replace "TODO_SET_REVIEWER_SUBAGENT" with "code-reviewer" and
// replace "TODO_SET_RESEARCHER_SUBAGENT" with "researcher".
// ============================================================================

// Code review agent - focused context (Slide 34)
Task(
  description: "Code review",
  prompt: "Review this PR focusing only on security, performance, and model-free T/R encapsulation",
  subagent_type: "TODO_SET_REVIEWER_SUBAGENT"
)

// Research agent - broad architectural query (Slide 34)
Task(
  description: "Research implementation",
  prompt: "Compare epsilon-greedy vs optimistic exploration f(u,n)=u+k/n for the 4x4 vacuum grid",
  subagent_type: "TODO_SET_RESEARCHER_SUBAGENT"
)
```

---

## 3. Domain Isolation Boundary: 4x4 Vacuum Grid with Unknown $T$ and $R$
```text
Row \ Col    0        1        2        3
   0      [start]  [  0  ]  [  0  ]  [  0  ]
   1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
   2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
   3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
```
- **Strict Object Encapsulation**: `VacuumGridEnv` (`src/environment.py`) isolates the private transition probabilities (`0.8` intended, `0.1` slip left, `0.1` slip right) and reward table (`+10.0` at `(3,3)`, `-1.0` at `(3,1)`, `living_reward` elsewhere) from `TabularQLearningAgent` (`src/agent.py`).
- **Branch Isolation (`PreToolUse` Hook)**: `.claude/settings.json` invokes `scripts/prevent-main-commit.sh` to isolate the `main` branch from direct agent commits.

---

## 4. Cross-Reference: Dynamic Context Imports (Supported Alongside Strategy 4)
<!--
TODO (Part 2C - Dynamic Context Imports, Slide 25):
Uncomment or add the three `@./context/*.md` lines below so Claude Code dynamically
loads the modular environment, Q-learning, and exploration context files:
  @./context/environment.md
  @./context/q-learning.md
  @./context/exploration.md
-->
