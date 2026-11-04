# Exploration vs. Exploitation Context (`@./context/exploration.md`)

## Exploration Strategies (CS 440 RL-L2 Lecture)
1. **Epsilon-Greedy ($\epsilon$-greedy)**:
   - With probability $\epsilon$, select a uniform random action $a \in \{\text{Up, Down, Left, Right}\}$.
   - With probability $1 - \epsilon$, select the greedy action $\arg\max_a Q(s, a)$ (breaking ties randomly).
2. **Optimistic Exploration Function**:
   - $f(u, n) = u + \frac{k}{n}$ where $u = Q(s', a')$, $n = N(s', a')$ visit count, and $k > 0$ is the exploration bonus.
   - Propagates optimism toward unvisited states and reduces cumulative **Regret**.
