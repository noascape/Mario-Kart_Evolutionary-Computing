# TECHNICAL_SPECS.md - Architecture & RAM Mapping

## RAM Addresses (Super Mario Kart - Repository Assets)
These addresses are decimal offsets from `0x7E0000` (WRAM), used by the `stable-retro` integration.

| Variable | Address (Dec) | Type | Notes |
| :--- | :--- | :--- | :--- |
| kart1_X | `136` | `<i2` | X Position |
| kart1_Y | `140` | `<i2` | Y Position |
| kart1_direction | `149` | `|u1` | Facing Angle |
| surface | `4270` | `|u1` | **64 = Road**. Others = Off-road/Grass |
| current_checkpoint | `4316` | `|u1` | Increments per track zone |
| lap | `4289` | `|u1` | Lap 128 = Lap 1 |
| totalCheckpoints | `328` | `|u1` | Mario Circuit 1 = 30 |
| kart1_speed | `4330` | `<i2` | Current velocity |

## Fitness Formula
The fitness is calculated cumulatively in `MarioKartWrapper`:
$$Fitness = \sum Reward$$

**Reward Calculation (per step):**
- **Checkpoint Progress:** $+100.0$ for each new increment in `progress`.
  - $progress = ((lap - 128) \cdot totalCheckpoints) + current\_checkpoint$
- **Speed Bonus:** $+(\frac{speed}{1000})$ if speed $> 100$ and not terminated.
- **Off-Road Penalty:** $-50.0$ if `surface != 64` (immediate termination).
- **Stagnation:** Episode terminates if `progress` does not increase for 300 steps.

**Initialization:**
- `self.max_progress` is set in `reset()` to prevent "free" points for the starting position.
