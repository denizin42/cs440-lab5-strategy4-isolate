# Q-Learning Context (`@./context/q-learning.md`)

## Model-Free Temporal-Difference Learning
Because $T(s,a,s')$ and $R(s,a,s')$ are unknown, offline MDP Value Iteration from Lab 3 cannot be used:
$$Q_{k+1}(s, a) \leftarrow \sum_{s'} T(s,a,s') [R(s,a,s') + \gamma \max_{a'} Q_k(s', a')] \quad \text{(Not possible without } T, R\text{)}$$

Instead, upon observing each sampled transition $(s, a, r, s', \text{done})$, update the action-value running average:
$$\text{sample} = r + \gamma \max_{a'} Q(s', a') \quad (\text{with } \max_{a'} Q(s', a') = 0 \text{ if } s' \text{ is terminal})$$
$$Q(s, a) \leftarrow (1 - \alpha) Q(s, a) + \alpha \cdot \text{sample}$$
