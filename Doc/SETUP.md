# Environment Setup & Verification

## 1. System Environment
- **OS:** Linux (Ubuntu/Debian recommended).
- **Display:** Headless rendering via `Xvfb`.
- **Python:** Version 3.11+.

## 2. Dependencies

### System Packages (installed via apt-get)
```bash
sudo apt-get update && sudo apt-get install -y \
    xvfb \
    python3-opengl \
    libsdl2-dev \
    libglu1-mesa-dev \
    freeglut3-dev \
    mesa-common-dev
```

### Python Packages (installed via pip)
```bash
pip install -r requirements.txt
```
Key packages include:
- `stable-retro`: SNES emulator (Farama Foundation fork).
- `neat-python`: Genetic algorithm framework.
- `gymnasium`: Environment interface.
- `pytest`: Testing framework.

## 3. ROM Import
Ensure your `Super Mario Kart (USA).sfc` file is in the `rom/` folder, then run:
```bash
sudo /usr/local/python/current/bin/python3.11 -m stable_retro.import rom/
```

## 4. Verification
Run the following command to ensure the emulator and rendering are working correctly:
```bash
PYTHONPATH=. xvfb-run -a pytest tests/test_environment.py tests/test_wrapper.py
```
A successful run should output `2 passed`.
