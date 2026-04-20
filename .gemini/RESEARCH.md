# RESEARCH.md - Super Mario Kart Evolution Log

## Evolutionary Experiments
### Experiment 1: Baseline NEAT (Visual Inputs) - DEPRECATED
- **Date:** 2026-04-20
- **Result:** Search space too large ($49,152+$ connections). Evolution stalled.

### Experiment 2: Optimized NEAT (RAM-Based)
- **Date:** 2026-04-20
- **Representation:** NEAT (4 RAM inputs: X, Y, Angle, Status)
- **State Initialization:** `start_race.state` (Exact 00:00:00 start).
- **Fitness Function:** Cumulative Euclidean distance from previous RAM (x, y) coordinates.
- **Formula:**
$$Fitness = \sum \sqrt{(x_{curr} - x_{prev})^2 + (y_{curr} - y_{prev})^2}$$
- **Hyperparameters:** Population 50, generations 100, biased 'Gas' activation threshold (0.4).

## Findings
- **RAM Mapping Success:** Coordinates `x` (7E0088) and `y` (7E008C) verified and active.
- **Fitness Breakthrough:** Switching to a 4-input RAM approach resulted in a fitness jump from 0.0 to 241.84 in 100 generations.
- **Navigation Scripting:** Perfect `start_race.state` achieved by tightening menu navigation timing (Lakitu green light at capture).
- **Coordinate Overflow:** Fixed a bug where `uint16` coordinate subtraction caused overflow; casting to `float` resolved it.

