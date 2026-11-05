"""Black-box 4x4 Vacuum World simulator with encapsulated T(s,a,s') and R(s,a,s').

Topology (from CLAUDE.md and @./context/environment.md):
    Row \\ Col    0        1        2        3
       0      [start]  [  0  ]  [  0  ]  [  0  ]
       1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
       2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
       3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
"""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

State = Tuple[int, int]
Action = str

ACTIONS: Tuple[Action, ...] = ("Up", "Down", "Left", "Right")

_ACTION_DELTAS: Dict[Action, Tuple[int, int]] = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1),
}

_LATERAL_SLIPS: Dict[Action, Tuple[Action, Action]] = {
    "Up": ("Left", "Right"),
    "Down": ("Right", "Left"),
    "Left": ("Down", "Up"),
    "Right": ("Up", "Down"),
}


class VacuumGridEnv:
    """Black-box 4x4 Vacuum World environment simulator.

    Transition probabilities T(s, a, s') and reward function R(s, a, s') are
    encapsulated as private attributes so the Q-learning agent can only observe
    sampled transitions (next_state, reward, done) via step(action).
    """

    rows: int = 4
    cols: int = 4
    start_state: State = (0, 0)
    obstacle_state: State = (1, 1)
    trap_state: State = (3, 1)
    goal_state: State = (3, 3)

    def __init__(self, living_reward: float = -0.04, seed: int = 42) -> None:
        """Initialize the 4x4 Vacuum Grid simulator with encapsulated dynamics."""
        self._living_reward: float = living_reward
        self._rng: random.Random = random.Random(seed)
        self._intent_prob: float = 0.80
        self._slip_left_prob: float = 0.10
        self._terminal_rewards: Dict[State, float] = {
            self.trap_state: -1.0,
            self.goal_state: 10.0,
        }
        self._current_state: State = self.start_state

    def reset(self) -> State:
        """Reset the robot to the start state (0, 0) and return the state."""
        self._current_state = self.start_state
        return self._current_state

    def is_terminal(self, state: State) -> bool:
        """Return True if the given state is a terminal state."""
        return state in self._terminal_rewards

    def get_valid_states(self) -> List[State]:
        """Return all valid non-obstacle states on the 4x4 grid."""
        return [
            (row, col)
            for row in range(self.rows)
            for col in range(self.cols)
            if (row, col) != self.obstacle_state
        ]

    def step(self, action: Action) -> Tuple[State, float, bool]:
        """Execute an action and return (next_state, reward, done)."""
        if action not in ACTIONS:
            raise ValueError(f"Unknown action: {action!r}. Expected one of {ACTIONS}.")

        if self.is_terminal(self._current_state):
            return self._current_state, 0.0, True

        actual_action = self._sample_noisy_action(action)
        next_state = self._apply_move(self._current_state, actual_action)
        self._current_state = next_state

        done = self.is_terminal(next_state)
        reward = self._terminal_rewards.get(next_state, self._living_reward)
        return next_state, reward, done

    def _sample_noisy_action(self, intended_action: Action) -> Action:
        """Sample the executed direction using 0.8 intended, 0.1 left, 0.1 right."""
        roll = self._rng.random()
        slip_left, slip_right = _LATERAL_SLIPS[intended_action]
        if roll < self._intent_prob:
            return intended_action
        if roll < self._intent_prob + self._slip_left_prob:
            return slip_left
        return slip_right

    def _apply_move(self, state: State, executed_action: Action) -> State:
        """Move one cell if within bounds and not hitting Obstacle X at (1, 1)."""
        d_row, d_col = _ACTION_DELTAS[executed_action]
        candidate: State = (state[0] + d_row, state[1] + d_col)
        in_bounds = 0 <= candidate[0] < self.rows and 0 <= candidate[1] < self.cols
        if not in_bounds or candidate == self.obstacle_state:
            return state
        return candidate
