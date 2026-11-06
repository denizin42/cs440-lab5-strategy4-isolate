"""Unit tests for the 4x4 Vacuum World Tabular Q-Learning implementation in src/."""

from __future__ import annotations

from src.agent import QLearningHyperparameters, TabularQLearningAgent
from src.environment import ACTIONS, VacuumGridEnv
from src.q_learning import run_hyperparameter_sweep, train_q_learning


def test_environment_topology_and_terminal_boundaries() -> None:
    """Verify 4x4 Vacuum Grid start, obstacle, trap, and goal coordinates."""
    env = VacuumGridEnv(living_reward=-0.04, seed=42)
    assert env.reset() == (0, 0)
    assert env.obstacle_state == (1, 1)
    assert env.trap_state == (3, 1)
    assert env.goal_state == (3, 3)
    assert (1, 1) not in env.get_valid_states()
    assert len(env.get_valid_states()) == 15
    assert env.is_terminal((3, 1))
    assert env.is_terminal((3, 3))
    assert not env.is_terminal((0, 0))


def test_bellman_terminal_update_does_not_bootstrap() -> None:
    """Verify Q(s, a) update uses 0.0 future value when done=True."""
    env = VacuumGridEnv(living_reward=-0.04, seed=42)
    params = QLearningHyperparameters(
        living_reward=-0.04,
        discount_gamma=0.90,
        learning_rate_alpha=0.10,
        exploration_epsilon=0.20,
    )
    agent = TabularQLearningAgent(states=env.get_valid_states(), hyperparameters=params)
    for act in ACTIONS:
        agent.q_table[((3, 3), act)] = 99.0

    agent.update(
        state=(2, 3),
        action="Down",
        reward=10.0,
        next_state=(3, 3),
        done=True,
    )
    assert abs(agent.q_table[((2, 3), "Down")] - 1.0) < 1e-9


def test_q_learning_converges_to_goal_avoiding_trap() -> None:
    """Verify trained policy reaches +10 goal at (3,3) and avoids -1 trap at (3,1)."""
    params = QLearningHyperparameters()
    env, agent, returns = train_q_learning(
        hyperparameters=params,
        exploration_mode="epsilon_greedy",
        episodes=3000,
        seed=42,
    )
    assert sum(returns[-200:]) / 200.0 > 7.5
    assert agent.greedy_action((3, 2)) == "Right"
    assert agent.greedy_action((2, 3)) == "Down"
    assert agent.greedy_action((3, 0)) == "Up"
    assert agent.state_value((2, 3)) > agent.state_value((0, 0)) > 0.0
    assert env.goal_state == (3, 3)


def test_hyperparameter_sensitivity_sweep() -> None:
    """Verify varying living_reward, gamma, alpha, and epsilon shifts V(s) and pi*(s)."""
    rows, _, extreme_agent = run_hyperparameter_sweep(episodes=1500)
    assert len(rows) == 9
    by_label = {row.label: row for row in rows}
    baseline = by_label["Baseline (r=-0.04, g=0.90, a=0.10, e=0.20)"]
    myopic = by_label["Discount gamma = 0.50 (Myopic Horizon)"]
    far_sighted = by_label["Discount gamma = 0.99 (Far-Sighted)"]
    assert myopic.v_start < baseline.v_start < far_sighted.v_start
    assert baseline.policies[0] == "Up"
    assert extreme_agent.greedy_action((1, 0)) == "Down"
    assert extreme_agent.greedy_action((3, 0)) == "Right"
