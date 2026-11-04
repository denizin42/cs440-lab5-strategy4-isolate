"""Black-Box 4x4 Vacuum Robot Environment with Encapsulated T(s, a, s') and R(s, a, s').

Unlike Lab 3 (Offline MDP Value Iteration), the learning agent in Lab 4 / Lab 5 does NOT
have access to the transition model T(s, a, s') or reward function R(s, a, s').
All internal dynamics are encapsulated as private attributes, and the agent can only
sample transitions (state, action, reward, next_state, done) via `step(action)`.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Final, Literal, Tuple

GridCoordinate = Tuple[int, int]
Action = Literal["Up", "Down", "Left", "Right"]

VALID_ACTIONS: Final[Tuple[Action, ...]] = ("Up", "Down", "Left", "Right")
ACTION_ARROWS: Final[dict[Action, str]] = {
    "Up": "^",
    "Down": "v",
    "Left": "<",
    "Right": ">",
}


@dataclass(frozen=True)
class StepOutcome:
    """Single sampled transition tuple returned by the black-box environment."""

    state: GridCoordinate
    action: Action
    next_state: GridCoordinate
    reward: float
    done: bool
    transition_outcome: str  # "as planned" or "slipped"


class VacuumGridEnv:
    """Stochastic 4x4 Vacuum Robot Grid Environment (Black-Box Simulator).

    Grid Layout (Row, Col):
        Row \\ Col    0        1        2        3
           0      [start]  [  0  ]  [  0  ]  [  0  ]
           1      [  0  ]  [  X  ]  [  0  ]  [  0  ]
           2      [  0  ]  [  0  ]  [  0  ]  [  0  ]
           3      [  0  ]  [ -1  ]  [  0  ]  [ +10 ]
    """

    START_STATE: Final[GridCoordinate] = (0, 0)
    OBSTACLE_STATE: Final[GridCoordinate] = (1, 1)
    TRAP_STATE: Final[GridCoordinate] = (3, 1)
    RECHARGE_STATE: Final[GridCoordinate] = (3, 3)

    TRAP_REWARD: Final[float] = -1.0
    RECHARGE_REWARD: Final[float] = 10.0

    _ACTION_DELTAS: Final[dict[Action, GridCoordinate]] = {
        "Up": (-1, 0),
        "Down": (1, 0),
        "Left": (0, -1),
        "Right": (0, 1),
    }

    _PERPENDICULAR_SLIPS: Final[dict[Action, Tuple[Action, Action]]] = {
        "Up": ("Left", "Right"),
        "Down": ("Right", "Left"),
        "Left": ("Down", "Up"),
        "Right": ("Up", "Down"),
    }

    def __init__(
        self,
        living_reward: float = -0.04,
        intended_prob: float = 0.8,
        slip_left_prob: float = 0.1,
        slip_right_prob: float = 0.1,
        seed: int | None = 42,
    ) -> None:
        """Initialize the black-box 4x4 vacuum environment.

        Args:
            living_reward: Step reward received on entering any non-terminal cell.
            intended_prob: Probability of moving in the intended direction (hidden from agent).
            slip_left_prob: Probability of slipping 90 degrees left (hidden from agent).
            slip_right_prob: Probability of slipping 90 degrees right (hidden from agent).
            seed: Optional random seed for reproducible stochastic transitions.
        """
        self._rows: int = 4
        self._cols: int = 4
        self._living_reward: float = float(living_reward)
        self._transition_weights: Tuple[float, float, float] = (
            intended_prob,
            slip_left_prob,
            slip_right_prob,
        )
        self._rng: random.Random = random.Random(seed)
        self._current_state: GridCoordinate = self.START_STATE

    @property
    def rows(self) -> int:
        """Number of grid rows."""
        return self._rows

    @property
    def cols(self) -> int:
        """Number of grid columns."""
        return self._cols

    @property
    def current_state(self) -> GridCoordinate:
        """Current (row, col) position of the vacuum robot."""
        return self._current_state

    def all_valid_states(self) -> list[GridCoordinate]:
        """Return all valid (non-obstacle) grid coordinates."""
        return [
            (row, col)
            for row in range(self._rows)
            for col in range(self._cols)
            if (row, col) != self.OBSTACLE_STATE
        ]

    def non_terminal_states(self) -> list[GridCoordinate]:
        """Return all non-terminal, non-obstacle grid coordinates."""
        return [
            state
            for state in self.all_valid_states()
            if not self.is_terminal(state)
        ]

    def is_terminal(self, state: GridCoordinate) -> bool:
        """Return True if `state` is the Trap (3, 1) or Recharge Goal (3, 3)."""
        return state in (self.TRAP_STATE, self.RECHARGE_STATE)

    def reset(self, start_state: GridCoordinate | None = None) -> GridCoordinate:
        """Reset the environment to the start state (or an optional valid state)."""
        if start_state is None:
            self._current_state = self.START_STATE
        else:
            if start_state == self.OBSTACLE_STATE:
                raise ValueError(f"Cannot reset into obstacle state {start_state}.")
            self._current_state = start_state
        return self._current_state

    def step(self, action: Action) -> StepOutcome:
        """Execute `action` in the stochastic environment and return the sampled outcome.

        The learning agent calls this method to observe `(next_state, reward, done)`
        without ever accessing private slip probabilities or reward tables.
        """
        if action not in VALID_ACTIONS:
            raise ValueError(f"Invalid action '{action}'. Must be one of {VALID_ACTIONS}.")

        if self.is_terminal(self._current_state):
            return StepOutcome(
                state=self._current_state,
                action=action,
                next_state=self._current_state,
                reward=0.0,
                done=True,
                transition_outcome="terminal",
            )

        previous_state = self._current_state
        slip_left, slip_right = self._PERPENDICULAR_SLIPS[action]
        candidate_Directions: Tuple[Action, Action, Action] = (action, slip_left, slip_right)

        chosen_direction: Action = self._rng.choices(
            candidate_Directions,
            weights=self._transition_weights,
            k=1,
        )[0]

        next_state = self._apply_move(previous_state, chosen_direction)
        planned_state = self._apply_move(previous_state, action)
        transition_outcome = "as planned" if next_state == planned_state else "slipped"

        reward = self._compute_reward(next_state)
        done = self.is_terminal(next_state)
        self._current_state = next_state

        return StepOutcome(
            state=previous_state,
            action=action,
            next_state=next_state,
            reward=reward,
            done=done,
            transition_outcome=transition_outcome,
        )

    def _apply_move(self, state: GridCoordinate, move: Action) -> GridCoordinate:
        """Compute resulting state after attempting a single directional move."""
        row, col = state
        delta_row, delta_col = self._ACTION_DELTAS[move]
        candidate_row = row + delta_row
        candidate_col = col + delta_col

        within_bounds = (0 <= candidate_row < self._rows) and (0 <= candidate_col < self._cols)
        if within_bounds and (candidate_row, candidate_col) != self.OBSTACLE_STATE:
            return (candidate_row, candidate_col)
        return state

    def _compute_reward(self, next_state: GridCoordinate) -> float:
        """Private reward lookup based on the state entered."""
        if next_state == self.RECHARGE_STATE:
            return self.RECHARGE_REWARD
        if next_state == self.TRAP_STATE:
            return self.TRAP_REWARD
        return self._living_reward
