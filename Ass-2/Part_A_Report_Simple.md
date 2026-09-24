# AIML ZG528 – Assignment 2
## Part A – Simple Viva Notes

Paper studied:
Deep Reinforcement Learning with Enhanced PPO for Safe Mobile Robot Navigation

Chosen domain:
Restaurant food delivery robot

---

## 1) What this paper is trying to do

The paper wants a robot to move from start to goal safely, without crashing.

It uses:
- LiDAR readings (to sense obstacles)
- Goal direction and robot pose info
- Reinforcement Learning (PPO)

Main idea:
Instead of building a full map and running A*/D* style planners, the robot directly learns which velocity commands to give at each step.

---

## 2) What mapless means (very important)

Mapless does NOT mean the robot is blind.

Mapless means:
- No pre-built global occupancy map is used for planning.
- No explicit SLAM map is maintained by the policy during navigation.
- Decisions are made from current local observations + goal/pose information.

So yes: no initial map is required in this approach.

---

## 3) Input and output of the learning policy

Input (state):
- Compressed LiDAR features
- Previous linear/angular velocity
- Goal-related direction info
- Robot yaw/heading terms

Output (action):
- Linear velocity v
- Angular velocity w

In short:
Policy reads local state and directly predicts control commands.

---

## 4) Why PPO + Residual Blocks

Why PPO:
- Stable RL algorithm for continuous control
- Safer policy updates than plain policy gradient

Why Residual Blocks:
- Better gradient flow in deeper networks
- Helps learning smoother and more reliable motion behavior

---

## 5) Reward design in simple words

The paper tests reward shaping to teach good behavior:
- Positive reward for moving toward goal
- Penalty when near obstacles
- Penalty for unsafe/collision behavior
- Reward for task completion

Effect:
Better reward shaping usually gives safer and more efficient navigation.

---

## 6) How this compares with classical robotics stack

Classical stack:
- Localization (AMCL)
- Mapping (SLAM)
- Global planner (A*/Dijkstra)
- Local planner (DWA/TEB)
- Controller (PID)

Paper’s learned stack:
- Collapses planning + control decisions into one learned policy

Trade-off:
- Classical: easier to explain/debug/certify
- Learned: less manual tuning, can adapt better in some complex settings

---

## 7) Main findings (high level)

Reported trend in the paper:
- Enhanced PPO (with residual blocks + reward shaping) performs better than weaker baselines in cluttered scenarios.
- DDPG baseline is less stable in harder environments.

Meaning for restaurant robots:
- Learned policy can be useful in narrow aisles/crowded layouts.
- But robust deployment still needs careful safety checks.

---

## 8) Limitations (critical appraisal)

1. Sim-to-real gap:
Results in Gazebo may not fully transfer to real restaurant floors.

2. Goal information assumption:
Goal direction is available from simulator transforms; real deployment may be noisier.

3. Limited sensing:
LiDAR-only compact state may miss semantic cues (people intent, reflective surfaces, etc.).

---

## 9) Viva-ready 30-second summary

This paper uses a mapless RL approach where a TurtleBot learns safe navigation from local LiDAR and goal/pose cues using PPO with residual networks. It removes explicit map-based planning and directly outputs velocity commands. In cluttered indoor settings, enhanced PPO with reward shaping shows better stability and success trends than weaker baselines. The method is promising for restaurant delivery robots, but real-world deployment still faces sim-to-real, safety, and observability challenges.

---

## 10) Viva Q&A quick prep

Q: Does mapless mean no sensors?
A: No. It means no explicit global map for planning; local sensors are still used.

Q: Does mapless mean no initial map known?
A: Yes, in the planning pipeline there is no required preloaded occupancy map.

Q: Why still mention pose/goal info then?
A: Because mapless removes map dependence, not all state dependence.

Q: When should we prefer classical stack?
A: When explainability, deterministic behavior, and certification are priorities.

Q: When can learned policy be preferred?
A: When environment variability is high and manual planner tuning cost is high.
