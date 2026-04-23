import os
import sys
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

from src.env.mario_kart_wrapper import MarioKartWrapper

custom_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration'))
retro.data.add_custom_integration(custom_path)

def check_initial_state():
    print("Checking initial state...")
    try:
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=os.path.abspath(os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')), 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        env = MarioKartWrapper(inner_env)
    except Exception as e:
        print(f"Failed to load environment: {e}")
        return

    obs, info = env.reset()
    
    # We need to manually calculate progress like the wrapper does in step()
    def get_val(name):
        fallbacks = {
            "checkpoint": (0x7E1020, "|u1"),
            "lap": (0x7E10C1, "|u1"),
            "total_checkpoints": (0x7E1162, "|u1")
        }
        addr, vtype = fallbacks[name]
        ram = env.unwrapped.get_ram()
        wram_addr = addr - 0x7E0000
        return ram[wram_addr]

    curr_checkpoint = get_val("checkpoint")
    curr_lap = get_val("lap")
    total_checkpoints = get_val("total_checkpoints")
    
    rel_lap = curr_lap - 127 if curr_lap >= 127 else 0
    progress = (rel_lap * (total_checkpoints if total_checkpoints > 0 else 26)) + curr_checkpoint
    
    print(f"Initial State:")
    print(f"  Lap (Raw): {curr_lap}")
    print(f"  Checkpoint: {curr_checkpoint}")
    print(f"  Total Checkpoints: {total_checkpoints}")
    print(f"  Relative Lap: {rel_lap}")
    print(f"  Initial Progress: {progress}")
    
    # Take one step with Gas
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1
    obs, reward, terminated, truncated, info = env.step(action)
    
    print(f"\nAfter 1 Step:")
    print(f"  Reward: {reward}")
    print(f"  Info Progress: {info.get('progress')}")
    print(f"  Info Lap: {info.get('lap')}")
    print(f"  Info Checkpoint: {info.get('checkpoint')}")

    env.close()

if __name__ == "__main__":
    check_initial_state()
