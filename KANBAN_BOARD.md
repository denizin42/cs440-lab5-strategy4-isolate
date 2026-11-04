# CS 440 Lab 5 — Group 2 Combined Kanban Board

**Team Members:** David Jablonski (`@denizin42`), Chris Mills (`@chris-mills03`), James Richardson (`@RichardsonJC`)  
**Repositories Covered by This Board:**
1. **Strategy 1 (Write) + All 4 Features:** [`denizin42/cs440-lab5-strategy1-write`](https://github.com/denizin42/cs440-lab5-strategy1-write)
2. **Strategy 4 (Isolate) + All 4 Features:** [`denizin42/cs440-lab5-strategy4-isolate`](https://github.com/denizin42/cs440-lab5-strategy4-isolate)

---

## Kanban Overview

| ID | Card Title | Feature / Scope | Suggested Owner | Verification Command | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **#0** | Scaffold `VacuumGridEnv`, CLI Runner, & Pytest Suite | Environment & Harness | `@denizin42` | `pytest --collect-only` | **Done** |
| **#1** | **Part 1:** Q-Learning Math & Hyperparameters (`src/agent.py`) | Core RL Solution | `@RichardsonJC` / `@denizin42` | `pytest -v -k TestPart1QLearning` | **To Do** |
| **#2** | **Part 2:** Feature 1 — Hooks & Dynamic Memory (`.claude/settings.json`, `scripts/context-switcher.sh`, `CLAUDE.md`) | Strategy 1 (Write) + Hooks | `@chris-mills03` | `pytest -v -k TestPart2HooksAndMemory` | **To Do** |
| **#3** | **Part 3:** Feature 3 — On-Demand Audit Skill (`.claude/skills/q-learning-audit/SKILL.md`) | Strategy 1 (Write) + Skills | `@chris-mills03` | `pytest -v -k TestPart3Skills` | **To Do** |
| **#4** | **Part 4:** Feature 4 — Isolated Sub-Agents (`.claude/agents/*.md`, `CLAUDE.md`) | Strategy 4 (Isolate) + Sub-Agents | `@RichardsonJC` | `pytest -v -k TestPart4SubAgents` | **To Do** |
| **#5** | **Part 5:** Feature 2 — FastMCP Server (`mcp_server.py`) | MCP Tools, Resources & Prompts | `@denizin42` | `pytest -v -k TestPart5MCP` | **To Do** |
| **#6** | **Part 6:** Sync Both Repos & Record 3-Minute Group Video | Final Deliverables | All Group 2 Members | `pytest -v && python3 -m src.q_learning` | **To Do** |

---

## Detailed Task Cards & Checklists

### Card #1 — Part 1: Q-Learning Math & Hyperparameters (`src/agent.py`)
- **Files:** `src/agent.py`
- **Subtasks:**
  - [ ] **Part 1A (`Hyperparameters`):** Set `living_reward = -0.04`, `discount_gamma = 0.90`, `learning_rate_alpha = 0.10`, and `exploration_epsilon = 0.20`.
  - [ ] **Part 1B (`TabularQLearningAgent.select_action`):** Implement $\epsilon$-greedy action selection (`self._rng.random() < self.exploration_epsilon` $\rightarrow$ random choice from `VALID_ACTIONS`, else `self.greedy_action(state)`).
  - [ ] **Part 1C (`TabularQLearningAgent.update`):** Implement the Bellman TD update:
    $$\text{sample} = r + \gamma \max_{a'} Q(s', a') \quad (\text{with } \max_{a'} Q(s', a') = 0.0 \text{ when } \text{done} = \text{True})$$
    $$Q(s, a) \leftarrow (1 - \alpha) Q(s, a) + \alpha \cdot \text{sample}$$
- **Acceptance Test:**
  ```bash
  pytest -v -k TestPart1QLearning
  ```

---

### Card #2 — Part 2: Feature 1 — Hooks & Dynamic Memory (Strategy 1: Write)
- **Files:** `.claude/settings.json`, `scripts/context-switcher.sh`, `CLAUDE.md`
- **Subtasks:**
  - [ ] **Part 2A (`.claude/settings.json`):** Replace `TODO_PART_2A` under `UserPromptSubmit` with `bash "$CLAUDE_PROJECT_DIR/scripts/context-switcher.sh"`.
  - [ ] **Part 2B (`scripts/context-switcher.sh`):** Replace `return 1` in `add_context()` with the `grep -qxF` idempotency guard:
    ```bash
    grep -qxF "$context_ref" "$CLAUDE_MD" || echo "$context_ref" >> "$CLAUDE_MD"
    ```
  - [ ] **Part 2C (`CLAUDE.md`):** Uncomment the three `@./context/*.md` lines at the bottom of `CLAUDE.md`:
    ```markdown
    @./context/environment.md
    @./context/q-learning.md
    @./context/exploration.md
    ```
- **Acceptance Test:**
  ```bash
  pytest -v -k TestPart2HooksAndMemory
  ```

---

### Card #3 — Part 3: Feature 3 — On-Demand Audit Skill (Strategy 1: Write)
- **Files:** `.claude/skills/q-learning-audit/SKILL.md`
- **Subtasks:**
  - [ ] **Part 3 (`SKILL.md`):** Complete the YAML frontmatter with `name: q-learning-audit` and a descriptive `description` explaining when Claude loads the skill to audit model-free $T$/$R$ encapsulation and terminal state boundaries.
- **Acceptance Test:**
  ```bash
  pytest -v -k TestPart3Skills
  ```

---

### Card #4 — Part 4: Feature 4 — Isolated Sub-Agents (Strategy 4: Isolate)
- **Files:** `.claude/agents/code-reviewer.md`, `.claude/agents/researcher.md`, `CLAUDE.md`
- **Subtasks:**
  - [ ] **Part 4A (`code-reviewer.md`):** Set YAML frontmatter (`name: code-reviewer`, `description`, `tools: ["Read", "Grep", "Glob"]`, `model: sonnet`).
  - [ ] **Part 4A (`researcher.md`):** Set YAML frontmatter (`name: researcher`, `description`, `tools: ["Read", "Grep"]`, `model: sonnet`).
  - [ ] **Part 4B (`CLAUDE.md`):** In Section 3 (`Task(...)`), set `subagent_type: "code-reviewer"` and `subagent_type: "researcher"`.
- **Acceptance Test:**
  ```bash
  pytest -v -k TestPart4SubAgents
  ```

---

### Card #5 — Part 5: Feature 2 — FastMCP Server (`mcp_server.py`)
- **Files:** `mcp_server.py`, `.mcp.json`
- **Subtasks:**
  - [ ] **Part 5A (`@mcp.tool` — `run_q_learning_experiment`):** Instantiate `Hyperparameters(...)`, run `env, agent = run_experiment(params)`, and return formatted utilities and policy grids.
  - [ ] **Part 5B (`@mcp.resource` — `get_hyperparameters_resource`):** Return a dictionary containing `living_reward`, `discount_gamma`, `learning_rate_alpha`, and `exploration_epsilon`.
  - [ ] **Part 5C (`@mcp.prompt` — `audit_hyperparameters_prompt`):** Return a reusable prompt string instructing Claude to call `run_q_learning_experiment` and verify the learned policy routes around Obstacle `X` at `(1, 1)` and Trap `-1` at `(3, 1)` to reach `+10` at `(3, 3)`.
- **Acceptance Test:**
  ```bash
  pytest -v -k TestPart5MCP
  ```

---

### Card #6 — Part 6: Sync Both Repositories & Record 3-Minute Group Video
- **Files:** `VIDEO_PRESENTATION_GUIDE.md`, `group_2.txt`
- **Subtasks:**
  - [ ] Run full test suite (`pytest -v`) and CLI demonstration (`python3 -m src.q_learning`).
  - [ ] Sync completed files between `cs440-lab5-strategy1-write` and `cs440-lab5-strategy4-isolate` and push both to GitHub.
  - [ ] Record the 3-minute group video with all 3 team members showing their faces and professional backgrounds, covering:
    1. Code feature decisions (Hooks, MCP, Skills, Sub-agents)
    2. Hyperparameter decisions (`living_reward = -0.04`, `gamma = 0.90`, `alpha = 0.10`, `epsilon = 0.20`)
    3. Live running solution (`python3 -m src.q_learning`)
  - [ ] Paste private video link into `group_2.txt` and submit on Canvas.
