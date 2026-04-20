# Tutorial: Implementing a New Evolutionary Representation

This guide explains how to add a new evolutionary approach (e.g., a "2D Gnome Matrix") to the Super Mario Kart evolution project.

## 1. Understanding Genome Representations

A **Genome Representation** defines how an agent's "brain" is encoded as data and how it processes information. Different representations are suitable for different levels of complexity:

*   **NEAT (NeuroEvolution of Augmenting Topologies):** This is the current default. It evolves both the **weights** and the **structure** (topology) of the network. It starts with a simple input-to-output mapping and adds neurons and connections over time. This is "Search-based structure evolution."
*   **Fixed Topology (e.g., Simple MLP):** The number of layers and neurons is decided beforehand (e.g., a 4-8-12 network). Only the weights are evolved. This is easier to implement but limits the network's ability to find its own optimal complexity.
*   **Matrix Representation:** Often used in "Grid-based" games. In this approach, you create a 2D grid (matrix) of the environment. Each "point" or cell in the matrix acts as a specific input sensor.
    *   **How it works:** Imagine a 10x10 grid around Mario. If a cell contains a wall, the input is `1`. If it's the track, the input is `0`. The network then has exactly 100 input neurons (one for every point in the matrix).
    *   **Direct Mapping:** You multiply this 100-element input vector by a weight matrix to produce your 12 button outputs.

### Training Different Representations
All representations follow the same evolutionary loop, but the "math" behind their mutation varies:
1.  **NEAT:** Uses the NEAT algorithm to add connections or nodes.
2.  **Matrix/Fixed:** Uses standard Genetic Algorithms (GA). Mutation simply adds small random numbers (Gaussian noise) to the weights in the matrix.
3.  **Approach Independence:** Not all representations use NEAT. NEAT is a specific *type* of representation and evolution strategy. You can use a Matrix representation with a simple GA instead.

## 2. Directory Structure
All representations must live in `src/evolution/representations/`. Create a new folder for your approach:

```text
src/evolution/representations/my_new_approach/
├── __init__.py
├── genome.py       # Your genome logic
└── evolution.py    # Your evolution engine logic
```

## 2. Implementing the Genome
Your genome class must inherit from `BaseGenome` in `src/evolution/base.py`.

### Key Methods:
- `get_action(observation)`: This is the most important method. It receives the environment state (Visuals and RAM) and must return a `np.ndarray` of 12 integers (0 or 1).
- `mutate()`: Define how your genome changes over generations.
- `save(file_path)` / `load(file_path)`: Logic for checkpointing.

**Example Template:**
```python
from src.evolution.base import BaseGenome
import numpy as np

class MyNewGenome(BaseGenome):
    def get_action(self, observation):
        ram = observation.get('ram_state', {})
        # Implement your logic here (Matrix math, logic gates, etc.)
        actions = np.zeros(12, dtype=np.int8)
        actions[0] = 1 # Example: Always accelerate
        return actions

    def mutate(self):
        # Implementation of mutation
        pass

    def save(self, file_path):
        # Implementation of serialization
        pass
```

## 3. Implementing the Evolution Engine
Your evolution class must inherit from `BaseEvolution`.

### Key Methods:
- `evaluate_generation(genomes, fitness_fn)`: Logic to run one cycle of evolution.
- `select_best(genomes)`: Logic to identify the top performer.

## 4. Integration with the Training Script
To make your representation accessible via `scripts/train.py`, you need to:
1. Ensure your classes follow the naming convention or are imported in the trainer.
2. Add a conditional block in `Trainer.run()` to handle your new `--rep` flag.

## 5. Testing (TDD)
Create a test file in `tests/` (e.g., `tests/test_my_new_approach.py`) to verify:
- `get_action` returns exactly 12 outputs.
- `mutate` actually changes the genome weights/values.
- `save` and `load` produce an identical genome.

## 6. Example: The 2D Gnome Matrix
If you are implementing a fixed-size weight matrix:
1. Define a `2D numpy array` in your Genome `__init__`.
2. In `get_action`, perform a dot product: `Output = Sigmoid(Inputs @ Matrix)`.
3. In `mutate`, add small random Gaussian noise to the matrix values.
