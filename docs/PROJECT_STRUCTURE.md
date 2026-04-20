# Proposed Project Structure

To maintain a clean and scalable evolutionary computing environment, the following directory structure is established:

```text
/workspaces/Mario-Kart_Evolutionary-Computing/
├── .gemini/             # Core plans, persistent research, and specification documents.
├── rom/                 # Mario Kart ROM file and its associated SHA1 hash.
├── src/                 # Main application logic.
│   ├── env/             # Custom Gymnasium wrappers and RAM mapping logic.
│   ├── evolution/       # NEAT population management, fitness, and training loops.
│   ├── visualization/   # Replay renderers and training telemetry plots.
│   └── main.py          # Entry point for training or evaluation runs.
├── tests/               # Unit and integration tests (TDD-first).
├── config/              # NEAT (.cfg) and environment configuration files.
├── Doc/                 # High-level architecture, setup guides, and project structure.
├── requirements.txt     # Python dependency definitions.
└── README.md            # Project overview and quick start.
```

## Architectural Rationale

### 1. Separation of Concerns
- **`src/env/`**: Isolates emulator-specific logic (RAM addresses, observation scaling) from the genetic algorithm.
- **`src/evolution/`**: Centralizes the NEAT population management, allowing for easy experimentation with different genetic parameters.

### 2. TDD-First Support
- **`tests/`**: Parallel to `src/`, providing an environment for rigorous validation of each component before implementation.

### 3. Configurability
- **`config/`**: Moving `.cfg` files from the root to this folder keeps the project organized as multiple NEAT topologies (feed-forward, recurrent) are tested.

### 4. Documentation
- **`Doc/`**: Serves as the primary source of truth for architecture and user guides, keeping the root directory uncluttered.
