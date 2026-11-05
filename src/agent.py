"""Model-free Tabular Q-Learning Agent for the 4x4 Vacuum World.

Implements Temporal-Difference Q-Learning (from @./context/q-learning.md) and
both epsilon-greedy and optimistic exploration f(u, n) = u + k / n
(from @./context/exploration.md and .claude/skills/q-learning-audit/SKILL.md).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.environment import ACTIONS, Action, State


@dataclass(frozen=True)
class QLearningHyperparameters:
    """Selected Q-learning hyperparameters specified in CLAUDE.md."""

    living_reward: float = -0.04
    discount_gamma: float = 0.90
    learning_rate_alpha: float = 0.10
    exploration_epsilon: float = 0.20
    optimistic_bonus_k: float = 2.0


class TabularQLearningAgent:
    """Model-free Tabular Q-Learning agent without access to T or R."""

    def __init__(
        self,
        states: List[State],
        hyperparameters: QLearningHyperparameters,
        exploration_mode: str = "epsilon_greedy",
        seed: int = 42,
    ) -> None:
        """Initialize Q-table Q(s, a) = 0.0 and visit counts N(s, a) = 0."""
        if exploration_mode not in {"epsilon_greedy", "optimistic"}:
            raise ValueError(
                f"Invalid exploration_mode: {exploration_mode!r}. "
                "Expected 'epsilon_greedy' or 'optimistic'."
            )
        self.hyperparameters: QLearningHyperparameters = hyperparameters
        self.exploration_mode: str = exploration_mode
        self._rng: random.Random = random.Random(seed)
        self.q_table: Dict[Tuple[State, Action], float] = {
            (state, action): 0.0 for state in states for action in ACTIONS
        }
        self.visit_counts: Dict[Tuple[State, Action], int] = {
            (state, action): 0 for state in states for action in ACTIONS
        }

    def select_action(self, state: State, training: bool = True) -> Action:
        """Select an action using epsilon-greedy or optimistic exploration."""
        if not training:
            return self.greedy_action(state)

        if self.exploration_mode == "optimistic":
            return self._select_optimistic_action(state)

        if self._rng.random() < self.hyperparameters.exploration_epsilon:
            return self._rng.choice(ACTIONS)
        return self.greedy_action(state)

    def greedy_action(self, state: State) -> Action:
        """Return argmax_a Q(s, a), breaking ties uniformly at random."""
        q_values = {action: self.q_table[(state, action)] for action in ACTIONS}
        max_q = max(q_values.values())
        best_actions = [
            action for action, val in q_values.items() if abs(val - max_q) <= 1e-12
        ]
        return self._rng.choice(best_actions)

    def _select_optimistic_action(self, state: State) -> Action:
        """Select argmax_a f(Q(s, a), N(s, a)) where f(u, n) = u + k / (n + 1)."""
        scores: Dict[Action, float] = {}
        for action in ACTIONS:
            utility = self.q_table[(state, action)]
            visits = self.visit_counts[(state, action)]
            scores[action] = utility + (
                self.hyperparameters.optimistic_bonus_k / float(visits + 1)
            )
        max_score = max(scores.values())
        best_actions = [
            action for action, val in scores.items() if abs(val - max_score) <= 1e-12
        ]
        return self._rng.choice(best_actions)

    def update(
        self,
        state: State,
        action: Action,
        reward: float,
        next_state: State,
        done: bool,
    ) -> float:
        """Apply the Bellman temporal-difference Q-learning update rule.

        When `done` is True (terminal state at (3, 1) or (3, 3)), the future
        value max_{a'} Q(s', a') is strictly 0.0 per q-learning-audit skill.
        """
        self.visit_counts[(state, action)] += 1
        current_q = self.q_table[(state, action)]
        max_next_q = (
            0.0
            if done
            else max(self.q_table[(next_state, next_act)] for next_act in ACTIONS)
        )
        sample = reward + self.hyperparameters.discount_gamma * max_next_q
        alpha = self.hyperparameters.learning_rate_alpha
        updated_q = (1.0 - alpha) * current_q + alpha * sample
        self.q_table[(state, action)] = updated_q
        return abs(updated_q - current_q)

    def state_value(self, state: State) -> float:
        """Return V(s) = max_a Q(s, a) for a state."""
        return max(self.q_table[(state, action)] for action in ACTIONS)
