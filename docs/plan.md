To ensure a clean and scalable architecture for comparing different evolutionary approaches, I have developed the following plan. This structure will enforce
  consistency while allowing for radical differences in internal logic (e.g., Matrix vs. NEAT).

  1. Proposed Directory Structure
  I will organize all algorithms under a dedicated representations folder:

    1 src/evolution/
    2 ├── base.py                 # Abstract Base Classes (Interfaces)
    3 └── representations/
    4     ├── template/           # The "Boilerplate" for new users
    5     │   ├── genome.py       # Action mapping logic
    6     │   ├── evolution.py    # Mutation/Crossover/Selection logic
    7     │   ├── fitness.py      # Representation-specific fitness tweaks
    8     │   └── config.py       # Hyperparameters
    9     └── neat_approach/      # Implementation using neat-python
   10         ├── genome.py
   11         ├── evolution.py
   12         └── ...

  2. The Implementation Template
  I will create a standardized interface (ABC) that every representation must implement:
   - get_action(observation): Must return the SNES button array.
   - mutate() / crossover(): Standardized hooks for the evolution engine.
   - save() / load(): For checkpointing.

  3. Master Training Script (scripts/train.py)
  A unified entry point with the following features:
   - Parallelization: Uses multiprocessing to run multiple SNES instances across all available CPU cores.
   - GPU Detection: Uses torch or tensorflow (if available) to detect hardware and pass a device flag to the representation.
   - Dynamic Loading: Allows you to run python scripts/train.py --rep neat_approach.

  4. TDD & Documentation
   - TDD: Every representation folder will require a matching test file in tests/evolution/ to verify that mutation produces valid genomes and actions are correctly
     mapped.
   - Documentation: I will create docs/TUTORIAL_NEW_REPRESENTATION.md which will be a step-by-step guide for a developer to implement Representation 3 (the 2D Gnome
     Matrix).

  5. Execution Strategy
   1. Define Interfaces: Create src/evolution/base.py.
   2. Build Template: Create the template/ folder with commented code.
   3. Implement NEAT: Move existing NEAT logic into the new neat_approach/ structure.
   4. Create CLI: Build the parallel training script.
   5. Verify: Run a test training session in the background.

  Does this plan meet your requirements? If so, I will begin by creating the interfaces and the template folder.