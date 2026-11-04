# Project Context: CS 440 Lab 5 — Vacuum Robot Q-Learning (Strategy 4: Isolate & All 4 Code Features)

## 1. Architecture & Problem Overview
This repository solves the **4x4 Vacuum Robot Reinforcement Learning** problem with unknown $T$ and $R$ using **Model-Free Tabular Q-Learning** and configures all 4 Claude Code features (**Hooks**, **MCP**, **Skills**, and **Sub-agents**).

### 4x4 Vacuum Grid World Specification
```text
Row \ Col    0        1        2        3
   0      [start]  [  0  ]  [  0  ]  [  0  ]
   1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
   2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
   3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
```
- **Start State `(0, 0)`**: Top-left corner (initial cell value `0`).
- **Obstacle `X` at `(1, 1)`**: Impassable wall/pillar; attempting to move into `(1, 1)` or outside the 4x4 boundary keeps the robot in its current state.
- **Terminal Trap `-1` at `(3, 1)`**: Hazard state yielding reward `-1.0` and ending the episode.
- **Terminal Recharge Goal `+10` at `(3, 3)`**: Goal state yielding reward `+10.0` and ending the episode.
- **Standard Cells `0`**: Non-terminal cells yielding the step/living reward (`living_reward`).

### Domain Rules: Unknown $T$ and $R$ (Model-Free RL Mandate)
- Unlike Lab 3 (Offline MDP Value Iteration), **we do NOT have the transition model $T(s, a, s')$ or the reward function $R(s, a, s')$**.
- The learning agent (`TabularQLearningAgent` in `src/agent.py`) MUST NOT access private environment transition probabilities or reward tables directly. All learning happens through sampled transitions $(s, a, r, s', \text{done})$ from `VacuumGridEnv.step(action)`.

---

## 2. Coding Standards (Strategy 1: Project Memory — Slide 22)
- Use Python 3.10+ with explicit PEP 484 type annotations.
- Use descriptive variable names (`learning_rate_alpha`, `discount_gamma`, `exploration_epsilon`, `living_reward`).
- Keep environment simulation state strictly encapsulated from the learning agent.
- Write deterministic unit tests using seeded random number generators before committing code.

---

## 3. Sub-Agent Delegation Rules (Strategy 4: Context Isolation — Slides 33–34)
You are the **Main Claude Agent (Orchestrator)**. To prevent **Context Confusion** and **Context Poisoning**, delegate specialized work through the **Context Filter** to the isolated sub-agents defined in `.claude/agents/`:

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

## 4. Dynamic Context Imports (Strategy 1: Write — Slides 21, 23, 25)
<!--
TODO (Part 2C - Dynamic Context Imports, Slide 25):
Uncomment or add the three `@./context/*.md` lines below so Claude Code dynamically
loads the modular environment, Q-learning, and exploration context files:
  @./context/environment.md
  @./context/q-learning.md
  @./context/exploration.md
-->
