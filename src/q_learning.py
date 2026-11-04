"""Main CLI Entry Point for CS 440 Lab 5: 4x4 Vacuum Robot Tabular Q-Learning.

Run from the repository root:
    python3 -m src.q_learning
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Tuple

# Support running both as `python3 -m src.q_learning` and `python3 src/q_learning.py`
if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import Hyperparameters, TabularQLearningAgent
from src.environment import (
    ACTION_ARROWS,
    Action,
    GridCoordinate,
    StepOutcome,
    VALID_ACTIONS,
    VacuumGridEnv,
)


def format_utilities_grid(
    env: VacuumGridEnv, utilities: Dict[GridCoordinate, float]
) -> str:
    """Format state utilities V(s) = max_a Q(s, a) as a 4x4 table matching Lab 3."""
    lines: List[str] = ["Learned State Utilities V(s) = max_a Q(s, a):"]
    for row in range(env.rows):
        cells: List[str] = []
        for col in range(env.cols):
            coord = (row, col)
            if coord == env.OBSTACLE_STATE:
                cells.append(f"{'X':>7}")
            elif coord == env.TRAP_STATE:
                cells.append(f"{'[-1]':>7}")
            elif coord == env.RECHARGE_STATE:
                cells.append(f"{'[+10]':>7}")
            else:
                cells.append(f"{utilities.get(coord, 0.0):>7.2f}")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def format_policy_grid(
    env: VacuumGridEnv, policy: Dict[GridCoordinate, Action]
) -> str:
    """Format the greedy policy pi(s) = argmax_a Q(s, a) with directional arrows."""
    lines: List[str] = [
        "Learned Greedy Policy (Legend: ^ Up, v Down, < Left, > Right, X Obstacle, T Trap, H Recharge):"
    ]
    for row in range(env.rows):
        cells: List[str] = []
        for col in range(env.cols):
            coord = (row, col)
            if coord == env.OBSTACLE_STATE:
                cells.append("X")
            elif coord == env.TRAP_STATE:
                cells.append("T")
            elif coord == env.RECHARGE_STATE:
                cells.append("H")
            else:
                cells.append(ACTION_ARROWS[policy[coord]])
        lines.append("   " + "   ".join(f"{cell:>2}" for cell in cells))
    return "\n".join(lines)


def format_q_table(
    env: VacuumGridEnv, agent: TabularQLearningAgent
) -> str:
    """Format the full Q(s, a) action-value table across all non-terminal states."""
    header = (
        f"{'State':<10} | {'Up (^)':>9} | {'Down (v)':>9} | "
        f"{'Left (<)':>9} | {'Right (>)':>9} | {'Best Action':<11}"
    )
    separator = "-" * len(header)
    lines: List[str] = ["Learned Q-Table Q(s, a):", separator, header, separator]
    q_snapshot = agent.q_table
    for state in env.non_terminal_states():
        action_vals = q_snapshot[state]
        best_act = max(VALID_ACTIONS, key=lambda act: action_vals[act])
        lines.append(
            f"{str(state):<10} | "
            f"{action_vals['Up']:>9.3f} | "
            f"{action_vals['Down']:>9.3f} | "
            f"{action_vals['Left']:>9.3f} | "
            f"{action_vals['Right']:>9.3f} | "
            f"{best_act:<5} ({ACTION_ARROWS[best_act]})"
        )
    lines.append(separator)
    return "\n".join(lines)


def simulate_policy_episode(
    policy: Dict[GridCoordinate, Action],
    living_reward: float = -0.04,
    start_state: GridCoordinate = VacuumGridEnv.START_STATE,
    max_steps: int = 50,
    seed: int = 1,
) -> Tuple[GridCoordinate, float, List[StepOutcome]]:
    """Run one stochastic rollout following the learned policy from `start_state`."""
    sim_env = VacuumGridEnv(living_reward=living_reward, seed=seed)
    state = sim_env.reset(start_state)
    total_reward = 0.0
    trajectory: List[StepOutcome] = []

    for _ in range(max_steps):
        if sim_env.is_terminal(state):
            break
        action = policy[state]
        outcome = sim_env.step(action)
        total_reward += outcome.reward
        trajectory.append(outcome)
        state = outcome.next_state

    return state, total_reward, trajectory


def evaluate_policy_reliability(
    policy: Dict[GridCoordinate, Action],
    living_reward: float = -0.04,
    num_eval_episodes: int = 200,
    base_seed: int = 1000,
) -> Dict[str, float]:
    """Evaluate policy success rate, trap rate, and average return over multiple rollouts."""
    successes = 0
    traps = 0
    total_rewards = 0.0
    total_steps = 0

    for idx in range(num_eval_episodes):
        final_state, ep_reward, trajectory = simulate_policy_episode(
            policy=policy,
            living_reward=living_reward,
            start_state=VacuumGridEnv.START_STATE,
            seed=base_seed + idx,
        )
        if final_state == VacuumGridEnv.RECHARGE_STATE:
            successes += 1
        elif final_state == VacuumGridEnv.TRAP_STATE:
            traps += 1
        total_rewards += ep_reward
        total_steps += len(trajectory)

    return {
        "recharge_rate_pct": (100.0 * successes) / num_eval_episodes,
        "trap_rate_pct": (100.0 * traps) / num_eval_episodes,
        "mean_reward": total_rewards / num_eval_episodes,
        "mean_steps": total_steps / num_eval_episodes,
    }


def run_experiment(hyperparameters: Hyperparameters) -> Tuple[VacuumGridEnv, TabularQLearningAgent]:
    """Train a TabularQLearningAgent on VacuumGridEnv with the specified hyperparameters."""
    env = VacuumGridEnv(
        living_reward=hyperparameters.living_reward,
        seed=hyperparameters.seed,
    )
    agent = TabularQLearningAgent(hyperparameters=hyperparameters)
    agent.train(env)
    return env, agent


def main() -> None:
    """CLI entry point displaying hyperparameters, Q-table, policy, and rollout logs."""
    defaults = Hyperparameters.__dataclass_fields__
    parser = argparse.ArgumentParser(
        description="CS 440 Lab 5: Model-Free Tabular Q-Learning for 4x4 Vacuum Robot"
    )
    parser.add_argument(
        "--living-reward",
        type=float,
        default=defaults["living_reward"].default,
        help="Living reward per non-terminal step (e.g., -0.04)",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=defaults["discount_gamma"].default,
        help="Discount factor gamma (e.g., 0.90)",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=defaults["learning_rate_alpha"].default,
        help="Learning rate alpha (e.g., 0.10)",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=defaults["exploration_epsilon"].default,
        help="Exploration rate epsilon (e.g., 0.20)",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=8000,
        help="Number of training episodes (default: 8000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible training (default: 42)",
    )
    args = parser.parse_args()

    hyperparameters = Hyperparameters(
        living_reward=args.living_reward,
        discount_gamma=args.gamma,
        learning_rate_alpha=args.alpha,
        exploration_epsilon=args.epsilon,
        num_episodes=args.episodes,
        seed=args.seed,
    )

    print("=" * 78)
    print("CS 440 Lab 5: 4x4 Vacuum Robot — Model-Free Tabular Q-Learning (Unknown T & R)")
    print("=" * 78)
    print("Selected Hyperparameters:")
    print(f"  - Living Reward (r_step)   : {hyperparameters.living_reward:+.2f}")
    print(f"  - Discount Factor (gamma)  : {hyperparameters.discount_gamma:.2f}")
    print(f"  - Learning Rate (alpha)    : {hyperparameters.learning_rate_alpha:.2f}")
    print(f"  - Exploration Rate (eps)   : {hyperparameters.exploration_epsilon:.2f}")
    print(f"  - Training Episodes        : {hyperparameters.num_episodes}")
    print("-" * 78)

    env, agent = run_experiment(hyperparameters)
    utilities = agent.extract_utilities(env)
    policy = agent.extract_policy(env)

    print(format_utilities_grid(env, utilities))
    print()
    print(format_policy_grid(env, policy))
    print()
    print(format_q_table(env, agent))
    print()

    final_state, total_reward, trajectory = simulate_policy_episode(
        policy=policy,
        living_reward=hyperparameters.living_reward,
        start_state=env.START_STATE,
        seed=1,
    )
    print(f"Sample Stochastic Rollout from Start State {env.START_STATE}:")
    print(f"  Step 0: Start               -> {env.START_STATE}")
    for step_idx, outcome in enumerate(trajectory, start=1):
        print(
            f"  Step {step_idx}: {outcome.action:<5} ({outcome.transition_outcome:<10}) "
            f"-> {outcome.next_state}  reward = {outcome.reward:+.2f}"
        )

    outcome_label = (
        "reached the recharger (+10)"
        if final_state == env.RECHARGE_STATE
        else "fell into trap (-1)"
        if final_state == env.TRAP_STATE
        else "ran out of steps"
    )
    print(
        f"Rollout Result: {outcome_label} at {final_state} in {len(trajectory)} moves, "
        f"total reward = {total_reward:+.2f}"
    )

    eval_metrics = evaluate_policy_reliability(
        policy=policy,
        living_reward=hyperparameters.living_reward,
    )
    print("-" * 78)
    print("Evaluation over 200 Stochastic Episodes from Start (0, 0):")
    print(f"  - Recharge Goal (+10) Rate : {eval_metrics['recharge_rate_pct']:.1f}%")
    print(f"  - Trap (-1) Collision Rate : {eval_metrics['trap_rate_pct']:.1f}%")
    print(f"  - Average Total Reward     : {eval_metrics['mean_reward']:+.2f}")
    print(f"  - Average Steps to Goal    : {eval_metrics['mean_steps']:.2f}")
    print("=" * 78)


if __name__ == "__main__":
    main()
