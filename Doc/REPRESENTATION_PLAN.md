# Genetic Representation & Architectural Plan

Based on the requirements in `specification.pdf` and the concepts in `brainstorm.pdf`, this document outlines the architecture, data provisioning, and evaluation metrics required to implement and fairly compare three distinct genetic representations in Super Mario Kart.

## 1. The "Evolution Bridge" Architecture

To support multiple representations without duplicating emulation code, we will implement an **Evolution Bridge** (`src/env/base_wrapper.py`). This layer must be agnostic to the genetic algorithm and provide multi-modal data.

### Multi-Modal Data Provisioning
Different representations require different types of inputs. The Bridge will provide three observation types:
1. **Visual State (`get_visual_state`):** Downsampled and grayscale frames (e.g., 64x64) suitable for Convolutional or large Feed-Forward Neural Networks.
2. **RAM State (`get_ram_state`):** Exact coordinates (X: `7E0088`, Y: `7E008C`), speed, and status/surface type (`7E10A6`). Suitable for tabular methods or state-matrix algorithms.
3. **Derived State (`get_raycast_state` - Optional):** Calculating distance to track edges based on X/Y and track geometry, providing a low-dimensional array for highly efficient neural networks.

---

## 2. Genomic Representations (The 3 Alternatives)

### Representation 1: Linear Weight Vector (Fixed Topology)
- **Concept:** A direct encoding where the genome is a 1D array of floating-point numbers representing the weights and biases of a fixed-size Neural Network.
- **Input:** Visual State or Derived State.
- **Selection:** Rank-Based Selection (prevents super-individuals from dominating early).
- **Mutation:** Gaussian Noise (additive tweaks to weights).
- **Crossover:** Uniform Crossover.

### Representation 2: NEAT-style Augmented Topology (Dynamic Structure)
- **Concept:** Evolves both the weights and the topology (nodes/connections) of the network, protecting structural innovations.
- **Input:** Visual State or Derived State.
- **Selection:** Tournament Selection with Speciation (protects new topologies).
- **Mutation:** Structural (Add Node, Add Connection) and Weight mutations.
- **Crossover:** Innovation-Based Crossover.

### Representation 3: 2D "Gnome" Matrix (State-Action Mappings)
- **Concept:** A non-neural representation treating the genome as a 2D matrix. Rows/columns correspond to discretized states (e.g., approaching a sharp left turn on dirt) and actions. A single column is a "gnome" representing a maneuver.
- **Input:** Quantized RAM State (discretized position, speed, and surface type).
- **Selection:** Elitism (top % carries over exactly, as precise racing lines are fragile).
- **Mutation:** Violated Directed Mutation (mutating entire "gnomes"/columns instead of single bits).
- **Crossover:** One-Point Matrix Crossover (swapping sequences of maneuvers).

---

## 3. Baselines for Comparison

As per the specification, we must implement two baselines:
1. **Naive Baseline:** Random action selection at each timestep to establish the absolute minimum performance threshold.
2. **Local Search Baseline:** A Hill Climbing or Simulated Annealing algorithm applied to the *Linear Weight Vector* representation, changing one parameter at a time and keeping it if performance improves.

---

## 4. Robust Fitness Function & Scaling

To ensure fair comparison across radically different representations (Matrix vs NEAT), the fitness function must be deterministic, exploit-proof, and invariant to the algorithm's internal mechanics.

### Composite Fitness Formula
Based on the brainstorm document, we will use a multi-objective formula:
$$f(x) = \alpha \cdot Progress + \beta \cdot AvgSpeed - \gamma \cdot WallCollisions - \delta \cdot OffRoadTime$$

- **Progress Tracking:** Measured by crossing invisible checkpoint lines (calculated via RAM X/Y coordinates) to prevent "reward farming" (driving in circles).
- **Death Penalty:** A harsh penalty for falling off the track or getting stuck.

### Scaling and Fair Comparison Metrics
Comparing a Matrix Genome to a NEAT population by "Generation" is fundamentally flawed because population sizes and evaluation times differ. 

**Standardized Metric:** The X-axis for all comparison graphs will be **Total Fitness Evaluations** (number of simulation runs), not Generations.
- **Performance Metric:** Maximum Fitness achieved.
- **Efficiency Metric:** Number of evaluations required to reliably complete Lap 1.
