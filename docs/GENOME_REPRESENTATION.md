# Custom Genome Representation & Training Guide

This document explains how to implement your own genetic representation and train it using the **Evolution Bridge**.

## 1. Creating a New Representation

To create a new representation (e.g., a "Gnome" Matrix or a custom Neural Network), follow these steps:

### Define your Genome Class
Your genome should encapsulate the data (weights, matrix, etc.) and provide a way to map inputs to actions.

```python
class MyCustomGenome:
    def __init__(self):
        # Initialize your representation (e.g., a 2D matrix)
        self.data = np.random.rand(10, 12) 

    def get_action(self, observation):
        # Logic to convert observation to SNES controller inputs
        # SNES buttons: [B, Y, SELECT, START, UP, DOWN, LEFT, RIGHT, A, X, L, R]
        return np.zeros(12, dtype=np.int8)
```

### Implement Mutation & Crossover
Ensure your evolution loop can mutate and combine these genomes.

## 2. Using the Evolution Bridge

The `EvolutionBridge` (`src/env/base_wrapper.py`) provides multi-modal data so you don't have to worry about RAM addresses or image processing.

```python
from src.env.base_wrapper import EvolutionBridge
import stable_retro as retro

# Initialize environment
inner_env = retro.make(game='SuperMarioKart-Snes-v0')
env = EvolutionBridge(inner_env)

# Get multi-modal data in the loop
obs, info = env.reset()

visual_data = info['visual_state']  # 64x64 grayscale
ram_data = info['ram_state']        # {'x', 'y', 'angle', 'status'}
ray_data = info['raycast_state']    # Low-dim distance sensors
```

## 3. Training Loop

A typical training iteration looks like this:

1. **Selection:** Choose the best performing genomes.
2. **Variation:** Apply mutation and crossover.
3. **Evaluation:**
   - For each genome, reset the `EvolutionBridge`.
   - Run the simulation for a fixed number of steps or until a stop condition.
   - Use `ram_data['x']` and `ram_data['y']` to calculate progress-based fitness.
4. **Repeat:** Continue until the stop condition (e.g., 5 laps) is met.

## 4. Fair Comparison

When comparing different representations, always use **Total Fitness Evaluations** as the X-axis in your plots to ensure fairness across algorithms with different population sizes.
