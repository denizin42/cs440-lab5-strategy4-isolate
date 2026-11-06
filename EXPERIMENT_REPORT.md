# CS 440 Lab 5 — 4x4 Vacuum World Model-Free Q-Learning Report

## 1. Selected Baseline Hyperparameters & MCP Verification
- **MCP Server Audit (`verify_hyperparameters`)**: `4 hyperparameter ranges are valid`
- **Living Reward (`living_reward`)**: `-0.04`
- **Discount Factor (`discount_gamma`, $\gamma$)**: `0.9`
- **Learning Rate (`learning_rate_alpha`, $\alpha$)**: `0.1`
- **Exploration Rate (`exploration_epsilon`, $\epsilon$)**: `0.2`
- **Optimistic Bonus ($k$ in $f(u,n)=u+k/(n+1)$)**: `2.0`

## 2. Baseline Results for Exploration Mode: `epsilon_greedy` (10,000 Episodes)
- **Total State-Action Updates**: `98,182`
- **Mean Training Return (First 500 Episodes)**: `+9.041`
- **Mean Training Return (Last 500 Episodes)**: `+9.448`
- **Greedy Policy Evaluation (1,000 Test Episodes, $\epsilon=0$)**: Mean Return = `+9.729`, Goal `(+10)` Reached = `100.0%`, Trap `(-1)` Hit = `0.0%`

### Learned State Utilities $V(s) = \max_a Q(s, a)$ & Policy $\pi^*(s)$
```text
Learned State Utilities V(s) = max_a Q(s, a):
   +5.043      +5.654      +6.535      +7.583  
   +4.274      [  X  ]     +7.312      +8.672  
   +3.920      +5.623      +8.575      +9.590  
   +1.094     -1.000(T)    +9.775    +10.000(G)

Learned Greedy Policy pi*(s) = argmax_a Q(s, a):
[  >  ]  [  >  ]  [  >  ]  [  v  ]
[  ^  ]  [  X  ]  [  v  ]  [  v  ]
[  ^  ]  [  >  ]  [  >  ]  [  v  ]
[  ^  ]  [ -1  ]  [  >  ]  [ +10 ]
```

### Full Action-Value Table $Q(s, a)$ and Visit Counts $N(s, a)$
| State `(r, c)` | `Q(s, Up)` (`N`) | `Q(s, Down)` (`N`) | `Q(s, Left)` (`N`) | `Q(s, Right)` (`N`) | `V(s) = max_a Q` | `pi*(s)` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `(0, 0)` | `+4.483` (`829`) | `+3.882` (`817`) | `+4.165` (`744`) | `+5.043` (`13386`) | `+5.043` | **Right** |
| `(0, 1)` | `+5.015` (`831`) | `+5.172` (`832`) | `+4.453` (`849`) | `+5.654` (`14008`) | `+5.654` | **Right** |
| `(0, 2)` | `+5.650` (`726`) | `+6.306` (`7044`) | `+5.216` (`715`) | `+6.535` (`5770`) | `+6.535` | **Right** |
| `(0, 3)` | `+6.409` (`362`) | `+7.583` (`5740`) | `+6.082` (`652`) | `+6.767` (`356`) | `+7.583` | **Down** |
| `(1, 0)` | `+4.274` (`2525`) | `+3.433` (`162`) | `+3.683` (`176`) | `+3.752` (`171`) | `+4.274` | **Up** |
| `(1, 2)` | `+5.949` (`496`) | `+7.312` (`7871`) | `+6.462` (`505`) | `+6.985` (`797`) | `+7.312` | **Down** |
| `(1, 3)` | `+6.543` (`409`) | `+8.672` (`6282`) | `+6.610` (`696`) | `+7.322` (`415`) | `+8.672` | **Down** |
| `(2, 0)` | `+3.920` (`201`) | `+0.362` (`26`) | `+2.127` (`26`) | `+2.823` (`32`) | `+3.920` | **Up** |
| `(2, 1)` | `+4.908` (`72`) | `+0.131` (`48`) | `+2.284` (`49`) | `+5.623` (`634`) | `+5.623` | **Right** |
| `(2, 2)` | `+6.742` (`456`) | `+8.134` (`2158`) | `+5.409` (`445`) | `+8.575` (`5701`) | `+8.575` | **Right** |
| `(2, 3)` | `+7.552` (`597`) | `+9.590` (`9769`) | `+7.949` (`550`) | `+8.588` (`569`) | `+9.590` | **Down** |
| `(3, 0)` | `+1.094` (`15`) | `-0.134` (`11`) | `-0.046` (`11`) | `-0.344` (`4`) | `+1.094` | **Up** |
| `(3, 1)` | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `-1.000` | **Trap (-1)** |
| `(3, 2)` | `+6.882` (`142`) | `+7.098` (`115`) | `+2.191` (`152`) | `+9.775` (`2233`) | `+9.775` | **Right** |
| `(3, 3)` | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `+10.000` | **Goal (+10)** |

## 2. Baseline Results for Exploration Mode: `optimistic` (10,000 Episodes)
- **Total State-Action Updates**: `81,257`
- **Mean Training Return (First 500 Episodes)**: `+8.353`
- **Mean Training Return (Last 500 Episodes)**: `+9.714`
- **Greedy Policy Evaluation (1,000 Test Episodes, $\epsilon=0$)**: Mean Return = `+9.725`, Goal `(+10)` Reached = `100.0%`, Trap `(-1)` Hit = `0.0%`

### Learned State Utilities $V(s) = \max_a Q(s, a)$ & Policy $\pi^*(s)$
```text
Learned State Utilities V(s) = max_a Q(s, a):
   +4.401      +5.202      +6.173      +6.887  
   +3.979      [  X  ]     +6.881      +8.236  
   +1.334      +3.961      +8.348      +9.378  
   +0.044     -1.000(T)    +9.486    +10.000(G)

Learned Greedy Policy pi*(s) = argmax_a Q(s, a):
[  >  ]  [  >  ]  [  >  ]  [  v  ]
[  ^  ]  [  X  ]  [  >  ]  [  v  ]
[  >  ]  [  >  ]  [  >  ]  [  v  ]
[  ^  ]  [ -1  ]  [  >  ]  [ +10 ]
```

### Full Action-Value Table $Q(s, a)$ and Visit Counts $N(s, a)$
| State `(r, c)` | `Q(s, Up)` (`N`) | `Q(s, Down)` (`N`) | `Q(s, Left)` (`N`) | `Q(s, Right)` (`N`) | `V(s) = max_a Q` | `pi*(s)` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `(0, 0)` | `-0.104` (`50`) | `-0.092` (`51`) | `-0.111` (`50`) | `+4.401` (`12518`) | `+4.401` | **Right** |
| `(0, 1)` | `-0.026` (`50`) | `-0.024` (`50`) | `-0.085` (`50`) | `+5.202` (`12625`) | `+5.202` | **Right** |
| `(0, 2)` | `+0.846` (`50`) | `+1.301` (`51`) | `+0.573` (`50`) | `+6.173` (`12515`) | `+6.173` | **Right** |
| `(0, 3)` | `+2.204` (`50`) | `+6.887` (`11077`) | `+1.705` (`50`) | `+2.275` (`50`) | `+6.887` | **Down** |
| `(1, 0)` | `+3.979` (`1614`) | `+0.329` (`50`) | `+0.457` (`50`) | `+0.688` (`50`) | `+3.979` | **Up** |
| `(1, 2)` | `+2.951` (`50`) | `+3.510` (`50`) | `+2.954` (`50`) | `+6.881` (`2791`) | `+6.881` | **Right** |
| `(1, 3)` | `+2.990` (`50`) | `+8.236` (`12354`) | `+2.571` (`50`) | `+4.204` (`50`) | `+8.236` | **Down** |
| `(2, 0)` | `+1.253` (`34`) | `+0.348` (`33`) | `+0.403` (`34`) | `+1.334` (`34`) | `+1.334` | **Right** |
| `(2, 1)` | `+2.392` (`29`) | `+0.242` (`29`) | `+0.787` (`29`) | `+3.961` (`30`) | `+3.961` | **Right** |
| `(2, 2)` | `+5.576` (`50`) | `+5.848` (`50`) | `+3.702` (`50`) | `+8.348` (`1548`) | `+8.348` | **Right** |
| `(2, 3)` | `+6.581` (`50`) | `+9.378` (`12269`) | `+5.791` (`50`) | `+8.284` (`50`) | `+9.378` | **Down** |
| `(3, 0)` | `+0.044` (`19`) | `-0.062` (`18`) | `-0.056` (`19`) | `-0.636` (`19`) | `+0.044` | **Up** |
| `(3, 1)` | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `-1.000` | **Trap (-1)** |
| `(3, 2)` | `+6.170` (`50`) | `+7.050` (`50`) | `+1.022` (`50`) | `+9.486` (`117`) | `+9.486` | **Right** |
| `(3, 3)` | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `0.000` (`0`) | `+10.000` | **Goal (+10)** |

## 3. Hyperparameter Sensitivity & Ablation Sweep (5,000 Episodes Each)

| Experiment Configuration | `r_living` | `$\gamma$` | `$\alpha$` | `$\epsilon$` | `$V(0,0)$` | `$\pi^*(1,0)$` | `$\pi^*(3,0)$` | Train Return (Last 500) | Greedy Eval Return | Goal `%` | Trap `%` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Baseline (r=-0.04, g=0.90, a=0.10, e=0.20) | `-0.04` | `0.90` | `0.10` | `0.20` | `+4.594` | **Up** | **Up** | `+9.486` | `+9.735` | `100.0%` | `0.0%` |
| Living Reward = -0.50 (Moderate Urgency) | `-0.50` | `0.90` | `0.10` | `0.20` | `+2.834` | **Down** | **Up** | `+5.362` | `+6.635` | `98.9%` | `1.1%` |
| Living Reward = -2.50 (Extreme Step Cost) | `-2.50` | `0.90` | `0.10` | `0.20` | `-6.587` | **Down** | **Right** | `-10.584` | `-6.673` | `83.4%` | `16.6%` |
| Discount gamma = 0.50 (Myopic Horizon) | `-0.04` | `0.50` | `0.10` | `0.20` | `+0.127` | **Down** | **Left** | `+8.694` | `+9.572` | `98.4%` | `1.6%` |
| Discount gamma = 0.99 (Far-Sighted) | `-0.04` | `0.99` | `0.10` | `0.20` | `+9.106` | **Up** | **Up** | `+9.414` | `+9.729` | `100.0%` | `0.0%` |
| Learning Rate alpha = 0.01 (Slow Updates) | `-0.04` | `0.90` | `0.01` | `0.20` | `+4.877` | **Down** | **Up** | `+9.302` | `+9.616` | `98.8%` | `1.2%` |
| Learning Rate alpha = 0.80 (High Variance) | `-0.04` | `0.90` | `0.80` | `0.20` | `+5.564` | **Up** | **Left** | `+9.256` | `+9.685` | `100.0%` | `0.0%` |
| Epsilon = 0.05 (Low Exploration) | `-0.04` | `0.90` | `0.10` | `0.05` | `+4.701` | **Up** | **Left** | `+9.470` | `+9.729` | `100.0%` | `0.0%` |
| Epsilon = 0.50 (High Random Regret) | `-0.04` | `0.90` | `0.10` | `0.50` | `+4.782` | **Down** | **Up** | `+8.016` | `+9.616` | `98.8%` | `1.2%` |

### Policy Shift Under Extreme Living Reward (`living_reward = -2.50`)
When `living_reward = -2.50` (worse than the `-1.0` Trap at `(3, 1)`), `(0, 0)` and `(1, 0)` flip from safe top-corridor routing (`>` / `^`) to cutting straight **Down** (`v`) along column 0 (incurring a `16.6%` trap rate), and `(3, 0)` flips from **Up** (`^`) to **Right** (`>`) to jump directly into the `-1.0` Trap rather than paying `-2.50` per step:
```text
Learned State Utilities V(s) = max_a Q(s, a):
   -6.587      -4.516      -1.702      +0.762  
   -4.565      [  X  ]     +2.138      +5.150  
   -1.986      +1.274      +5.130      +8.805  
   -1.799     -1.000(T)    +9.355    +10.000(G)

Learned Greedy Policy pi*(s) = argmax_a Q(s, a):
[  v  ]  [  >  ]  [  v  ]  [  v  ]
[  v  ]  [  X  ]  [  v  ]  [  v  ]
[  >  ]  [  >  ]  [  v  ]  [  v  ]
[  >  ]  [ -1  ]  [  >  ]  [ +10 ]
```

## 4. Strategy 4 (`researcher` Sub-Agent) Analysis Summary
- **Why Model-Free TD Q-Learning Is Required**: Because $T(s,a,s')$ and $R(s,a,s')$ are encapsulated inside `VacuumGridEnv`, offline Value Iteration ($\sum_{s'} T(s,a,s')[R + \gamma V(s')]$) cannot be computed. Tabular Q-Learning approximates the Bellman expectation from sampled transitions $(s, a, r, s', \text{done})$ using $Q(s,a) \leftarrow (1-\alpha)Q(s,a) + \alpha[r + \gamma \max_{a'} Q(s',a')]$.
- **Exploration vs. Exploitation ($\epsilon$-Greedy vs. Optimistic $f(u,n)$)**: Both policies converge to the optimal safe trajectory along the top/right corridor `(0,0) -> (0,1) -> (0,2) -> (1,2)/(0,3) -> (2,3) -> (3,3)` reaching the `+10` Recharge Goal **100.0%** of the time with **0.0%** Trap hits during greedy evaluation ($\epsilon=0$). While fixed $\epsilon=0.20$ incurs persistent random-action regret during training, optimistic exploration $f(u,n) = u + k/(n+1)$ systematically visits all state-action pairs early and then transitions to pure exploitation as $N(s,a)$ grows.
