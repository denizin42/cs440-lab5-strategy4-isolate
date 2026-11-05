"""Main runner for the CS 440 Lab 5 4x4 Vacuum World Q-Learning experiment.

Verifies the selected hyperparameters via the MCP server (`mcp_server.py`),
trains the model-free Tabular Q-Learning agent across both epsilon-greedy and
optimistic exploration strategies, and prints the learned state utilities V(s)
and optimal policy grid pi*(s).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from mcp_server import get_hyperparameters_resource, verify_hyperparameters
from src.agent import QLearningHyperparameters, TabularQLearningAgent
from src.environment import State, VacuumGridEnv

ARROW_SYMBOLS: Dict[str, str] = {
    "Up": "  ^  ",
    "Down": "  v  ",
    "Left": "  <  ",
    "Right": "  >  ",
}


def train_q_learning(
    hyperparameters: QLearningHyperparameters,
    exploration_mode: str = "epsilon_greedy",
    episodes: int = 5000,
    max_steps_per_episode: int = 100,
    seed: int = 42,
) -> Tuple[VacuumGridEnv, TabularQLearningAgent, List[float]]:
    """Train the Tabular Q-Learning agent on the 4x4 Vacuum Grid."""
    env = VacuumGridEnv(living_reward=hyperparameters.living_reward, seed=seed)
    agent = TabularQLearningAgent(
        states=env.get_valid_states(),
        hyperparameters=hyperparameters,
        exploration_mode=exploration_mode,
        seed=seed,
    )
    episode_returns: List[float] = []

    for _ in range(episodes):
        state = env.reset()
        total_reward = 0.0
        for _ in range(max_steps_per_episode):
            action = agent.select_action(state, training=True)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                break
        episode_returns.append(total_reward)

    return env, agent, episode_returns


def format_value_grid(env: VacuumGridEnv, agent: TabularQLearningAgent) -> str:
    """Format the 4x4 learned state-value table V(s) = max_a Q(s, a)."""
    lines: List[str] = ["Learned State Utilities V(s) = max_a Q(s, a):"]
    for row in range(env.rows):
        cells: List[str] = []
        for col in range(env.cols):
            state: State = (row, col)
            if state == env.obstacle_state:
                cells.append("   [  X  ] ")
            elif state == env.trap_state:
                cells.append("  -1.000(T)")
            elif state == env.goal_state:
                cells.append(" +10.000(G)")
            else:
                cells.append(f" {agent.state_value(state):+8.3f}  ")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def format_policy_grid(env: VacuumGridEnv, agent: TabularQLearningAgent) -> str:
    """Format the 4x4 greedy policy table pi*(s) = argmax_a Q(s, a)."""
    lines: List[str] = ["Learned Greedy Policy pi*(s) = argmax_a Q(s, a):"]
    for row in range(env.rows):
        cells: List[str] = []
        for col in range(env.cols):
            state: State = (row, col)
            if state == env.obstacle_state:
                cells.append("[  X  ]")
            elif state == env.trap_state:
                cells.append("[ -1  ]")
            elif state == env.goal_state:
                cells.append("[ +10 ]")
            else:
                best_action = agent.greedy_action(state)
                cells.append(f"[{ARROW_SYMBOLS[best_action]}]")
        lines.append("  ".join(cells))
    return "\n".join(lines)


def main() -> None:
    """Validate hyperparameters with MCP and execute the Q-learning experiment."""
    mcp_config = get_hyperparameters_resource()
    params = QLearningHyperparameters(
        living_reward=float(mcp_config["living_reward"]),
        discount_gamma=float(mcp_config["discount_gamma"]),
        learning_rate_alpha=float(mcp_config["learning_rate_alpha"]),
        exploration_epsilon=float(mcp_config["exploration_epsilon"]),
    )
    validation_msg = verify_hyperparameters(
        living_reward=params.living_reward,
        discount_gamma=params.discount_gamma,
        learning_rate_alpha=params.learning_rate_alpha,
        exploration_epsilon=params.exploration_epsilon,
    )
    print("=" * 74)
    print("CS 440 Lab 5 — 4x4 Vacuum World Model-Free Tabular Q-Learning")
    print("=" * 74)
    print(f"MCP Verification : {validation_msg}")
    print(
        f"Hyperparameters  : living_reward={params.living_reward}, "
        f"gamma={params.discount_gamma}, alpha={params.learning_rate_alpha}, "
        f"epsilon={params.exploration_epsilon}"
    )

    for mode in ("epsilon_greedy", "optimistic"):
        env, agent, returns = train_q_learning(
            hyperparameters=params,
            exploration_mode=mode,
            episodes=5000,
        )
        avg_last_500 = sum(returns[-500:]) / 500.0
        print("-" * 74)
        print(
            f"Exploration Mode : {mode} "
            f"(5,000 episodes | mean return last 500 eps: {avg_last_500:+.3f})"
        )
        print("-" * 74)
        print(format_value_grid(env, agent))
        print()
        print(format_policy_grid(env, agent))
    print("=" * 74)


if __name__ == "__main__":
    main()
