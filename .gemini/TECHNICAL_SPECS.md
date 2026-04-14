# TECHNICAL_SPECS.md - Architecture & RAM Mapping

## RAM Addresses (SNES Super Mario Kart)
| Variable | Address | Notes |
| :--- | :--- | :--- |
| East/West Position | `7E0088` | |
| North/South Position | `7E008C` | |
| Facing Angle | `7E10CA` | |
| Skid/Collision Status | `7E10A6` | |

## Fitness Formula
$$Fitness = \sum(\Delta Checkpoints) + Speed - Penalties$$
