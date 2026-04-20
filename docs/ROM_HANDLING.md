# ROM Handling Guide

This document provides instructions for setting up the Super Mario Kart ROM and its custom `stable-retro` integration.

## 1. ROM Details
- **File Name:** `Super Mario Kart (USA).sfc`
- **Location:** `rom/` directory.
- **SHA1 Hash:** `47e103d8398cf5b7cbb42b95df3a3c270691163b`

## 2. Custom Integration Setup

Since `SuperMarioKart-Snes-v0` is not part of the standard `stable-retro` package, a custom integration is used.

### Files Location
The integration files (RAM map, etc.) are located in:
`src/env/custom_integration/SuperMarioKart-Snes-v0/`

- `data.json`: Maps SNES RAM addresses to readable variables (e.g., `x`, `y`, `angle`).
- `metadata.json`: Basic emulator settings.
- `rom.sha`: Contains the ROM's SHA1 hash.

### Registration in Python
To use this custom integration, you must add it to the `stable-retro` data path before calling `retro.make()`:

```python
import os
import stable_retro as retro

# Add custom integration path
custom_path = os.path.abspath('src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

# Load the environment
env = retro.make(game='SuperMarioKart-Snes-v0')
```

## 3. Importing the ROM
After putting your `.sfc` file in the `rom/` folder, run the following command to register it with the emulator:

```bash
python3 -m stable_retro.import rom/
```

If it successfully matches the `rom.sha` in the custom integration, it will output:
`Imported 1 games`
