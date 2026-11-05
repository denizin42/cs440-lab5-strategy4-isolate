---
# ==============================================================================
# TODO (Part 3 - Claude Code Skill YAML Frontmatter, Slide 28):
# Set `name: q-learning-audit` and provide a clear `description` explaining when
# Claude should load this procedural skill on demand.
# ==============================================================================
name: q-learning-audit
description: Claude Code Skill YAML Frontmatter
---

# Q-Learning Compliance & Bellman Audit Skill (Slide 28)

Load this skill on demand when implementing or reviewing Q-learning code:

1. **Verify Model-Free Encapsulation (Unknown $T$ and $R$)**:
   - Confirm `TabularQLearningAgent` never reads private grid reward tables or slip probability weights directly from `VacuumGridEnv`.
2. **Verify Terminal State Boundary**:
   - When `next_state` is the Trap `(3, 1)` (`-1.0`) or Recharge Goal `(3, 3)` (`+10.0`), the future value term $\max_{a'} Q(s', a')$ must be `0.0`.
3. **Verify Tie-Breaking**:
   - When all $Q(s, a) == 0.0$ initially, break ties randomly rather than biasing toward a single direction.
