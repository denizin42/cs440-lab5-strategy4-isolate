"""Model-Free Tabular Q-Learning Agent for the 4x4 Vacuum Robot.

Implements Temporal-Difference (TD) Q-Learning without access to T(s, a, s') or R(s, a, s'):
    sample = r + discount_gamma * max_{a'} Q(s', a')   (0.0 if s' is terminal)
    Q(s, a) <- (1 - learning_rate_alpha) * Q(s, a) + learning_rate_alpha * sample
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Dict

from src.environment import Action, GridCoordinate, VALID_ACTIONS, VacuumGridEnv


@dataclass(frozen=True)
class Hyperparameters:
    """Selected Q-Learning hyperparameters for CS 440 Lab 5.

    ===========================================================================
    TODO (Part 1A - Select Hyperparameters):
    Replace the `None` placeholders below with your chosen float values:
      - living_reward       (e.g., -0.04 to match Lab 3 baseline living cost)
      - discount_gamma      (e.g., 0.90 so future +10 recharge reward propagates back)
      - learning_rate_alpha (e.g., 0.10 to smooth out 80/10/10 stochastic slips)
      - exploration_epsilon (e.g., 0.20 so the robot explores 20% of the time)
    ===========================================================================
    """

    living_reward: float = None  # TODO: Set living reward (e.g., -0.04)
    discount_gamma: float = None  # TODO: Set discount factor gamma in (0, 1] (e.g., 0.90)
    learning_rate_alpha: float = None  # TODO: Set learning rate alpha in (0, 1] (e.g., 0.10)
    exploration_epsilon: float = None  # TODO: Set epsilon in [0, 1] (e.g., 0.20)
    num_episodes: int = 8000
    max_steps_per_episode: int = 100
    seed: int = 42


class TabularQLearningAgent:
    """Model-Free Tabular Q-Learning Agent interacting solely via black-box transitions."""

    def __init__(
        self,
        hyperparameters: Hyperparameters,
        use_optimistic_exploration: bool = False,
        optimistic_bonus_k: float = 1.0,
    ) -> None:
        """Initialize Q-table Q(s, a) and visit counts N(s, a) to 0."""
        if (
            hyperparameters.living_reward is None
            or hyperparameters.discount_gamma is None
            or hyperparameters.learning_rate_alpha is None
            or hyperparameters.exploration_epsilon is None
        ):
            raise NotImplementedError(
                "TODO (Part 1A): Please set living_reward, discount_gamma, "
                "learning_rate_alpha, and exploration_epsilon in `Hyperparameters` (src/agent.py)."
            )

        self.hyperparameters: Hyperparameters = hyperparameters
        self.learning_rate_alpha: float = hyperparameters.learning_rate_alpha
        self.discount_gamma: float = hyperparameters.discount_gamma
        self.exploration_epsilon: float = hyperparameters.exploration_epsilon
        self.use_optimistic_exploration: bool = use_optimistic_exploration
        self.optimistic_bonus_k: float = optimistic_bonus_k

        self._rng: random.Random = random.Random(hyperparameters.seed)
        self._q_table: Dict[GridCoordinate, Dict[Action, float]] = {}
        self._visit_counts: Dict[GridCoordinate, Dict[Action, int]] = {}

    def _ensure_state_initialized(self, state: GridCoordinate) -> None:
        """Lazily initialize Q(s, a) = 0.0 and N(s, a) = 0 for all actions in `state`."""
        if state not in self._q_table:
            self._q_table[state] = {action: 0.0 for action in VALID_ACTIONS}
            self._visit_counts[state] = {action: 0 for action in VALID_ACTIONS}

    def get_q_value(self, state: GridCoordinate, action: Action) -> float:
        """Return current action-value estimate Q(state, action)."""
        self._ensure_state_initialized(state)
        return self._q_table[state][action]

    def get_state_value(self, state: GridCoordinate, is_terminal: bool = False) -> float:
        """Return V(s) = max_a Q(s, a), enforcing V(s) = 0.0 at terminal states."""
        if is_terminal:
            return 0.0
        self._ensure_state_initialized(state)
        return max(self._q_table[state].values())

    def select_action(self, state: GridCoordinate, training: bool = True) -> Action:
        """Select an action using epsilon-greedy (or optimistic exploration f(u, n) = u + k/n).

        =======================================================================
        TODO (Part 1B - Exploration vs. Exploitation, RL-L2 Lecture):
        Implement epsilon-greedy action selection:
        1. If `training` is True and a random float (`self._rng.random()`) is
           less than `self.exploration_epsilon`, return a uniformly random
           action from `VALID_ACTIONS` using `self._rng.choice(VALID_ACTIONS)`.
        2. Otherwise, return the greedy action via `self.greedy_action(state)`.
        =======================================================================
        """
        self._ensure_state_initialized(state)

        if training and self.use_optimistic_exploration:
            scored_actions: Dict[Action, float] = {}
            for action in VALID_ACTIONS:
                utility_u = self._q_table[state][action]
                visits_n = self._visit_counts[state][action]
                scored_actions[action] = (
                    utility_u + (self.optimistic_bonus_k / visits_n)
                    if visits_n > 0
                    else math.inf
                )
            max_score = max(scored_actions.values())
            best_actions = [
                act for act, score in scored_actions.items() if score == max_score
            ]
            return self._rng.choice(best_actions)

        # TODO (Part 1B): Replace the NotImplementedError below with your epsilon-greedy logic
        raise NotImplementedError(
            "TODO (Part 1B): Implement epsilon-greedy action selection in `select_action` (src/agent.py)."
        )

    def greedy_action(self, state: GridCoordinate) -> Action:
        """Return argmax_a Q(s, a) with random tie-breaking."""
        self._ensure_state_initialized(state)
        action_values = self._q_table[state]
        max_q = max(action_values.values())
        tied_best_actions = [
            action
            for action, q_val in action_values.items()
            if math.isclose(q_val, max_q, abs_tol=1e-12)
        ]
        return self._rng.choice(tied_best_actions)

    def update(
        self,
        state: GridCoordinate,
        action: Action,
        reward: float,
        next_state: GridCoordinate,
        done: bool,
        effective_alpha: float | None = None,
    ) -> float:
        """Perform the Model-Free Bellman Temporal-Difference (TD) Q-Learning update.

        =======================================================================
        TODO (Part 1C - Bellman TD Update, RL-L1 & RL-L2 Lectures):
        Given sampled transition `(state, action, reward, next_state, done)`:
        1. Increment `self._visit_counts[state][action] += 1`.
        2. Read current estimate: `current_q = self._q_table[state][action]`.
        3. Compute future value `max_next_q`:
           - If `done` is True (terminal state `(3, 1)` or `(3, 3)`), `max_next_q = 0.0`.
           - Otherwise, `max_next_q = max(self._q_table[next_state].values())`.
        4. Compute the TD target sample:
           `td_sample = reward + (self.discount_gamma * max_next_q)`
        5. Compute the running average update using `alpha`:
           `updated_q = ((1.0 - alpha) * current_q) + (alpha * td_sample)`
        6. Store `self._q_table[state][action] = updated_q` and return
           `abs(td_sample - current_q)`.
        =======================================================================
        """
        self._ensure_state_initialized(state)
        self._ensure_state_initialized(next_state)
        alpha = self.learning_rate_alpha if effective_alpha is None else effective_alpha

        # TODO (Part 1C): Replace the NotImplementedError below with the Bellman TD update
        raise NotImplementedError(
            "TODO (Part 1C): Implement the Bellman TD Q-learning update in `update` (src/agent.py)."
        )

    def train(self, env: VacuumGridEnv) -> list[float]:
        """Train the Q-learning agent on the black-box environment `env`."""
        for state in env.all_valid_states():
            self._ensure_state_initialized(state)

        non_terminal_states = env.non_terminal_states()
        episode_returns: list[float] = []
        total_episodes = self.hyperparameters.num_episodes

        for episode_idx in range(total_episodes):
            if episode_idx % 2 == 0:
                state = env.reset(env.START_STATE)
            else:
                state = env.reset(self._rng.choice(non_terminal_states))

            progress = episode_idx / max(1, total_episodes - 1)
            effective_alpha = self.learning_rate_alpha * max(0.05, 1.0 - 0.9 * progress)

            episode_reward = 0.0
            for _ in range(self.hyperparameters.max_steps_per_episode):
                action = self.select_action(state, training=True)
                outcome = env.step(action)
                self.update(
                    state=outcome.state,
                    action=outcome.action,
                    reward=outcome.reward,
                    next_state=outcome.next_state,
                    done=outcome.done,
                    effective_alpha=effective_alpha,
                )
                episode_reward += outcome.reward
                state = outcome.next_state
                if outcome.done:
                    break

            episode_returns.append(episode_reward)

        return episode_returns

    def extract_policy(self, env: VacuumGridEnv) -> Dict[GridCoordinate, Action]:
        """Extract the greedy policy pi(s) = argmax_a Q(s, a) for all non-terminal states."""
        policy: Dict[GridCoordinate, Action] = {}
        for state in env.non_terminal_states():
            self._ensure_state_initialized(state)
            action_values = self._q_table[state]
            policy[state] = max(VALID_ACTIONS, key=lambda act: action_values[act])
        return policy

    def extract_utilities(self, env: VacuumGridEnv) -> Dict[GridCoordinate, float]:
        """Extract state utilities V(s) = max_a Q(s, a) for all valid states."""
        utilities: Dict[GridCoordinate, float] = {}
        for state in env.all_valid_states():
            utilities[state] = self.get_state_value(
                state, is_terminal=env.is_terminal(state)
            )
        return utilities

    @property
    def q_table(self) -> Dict[GridCoordinate, Dict[Action, float]]:
        """Read-only snapshot of learned Q-values."""
        return {
            state: dict(actions) for state, actions in sorted(self._q_table.items())
        }

    @property
    def visit_counts(self) -> Dict[GridCoordinate, Dict[Action, int]]:
        """Read-only snapshot of state-action visit counts N(s, a)."""
        return {
            state: dict(counts) for state, counts in sorted(self._visit_counts.items())
        }
