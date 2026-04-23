import os
import sys
import numpy as np

# Ensure root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

from src.env.mario_kart_wrapper import MarioKartWrapper

# Register custom integration
custom_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration'))
retro.data.add_custom_integration(custom_path)

def verify():
    print("Initializing environment for RAM verification...")
    try:
        state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=state_path, 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        env = MarioKartWrapper(inner_env)
    except Exception as e:
        print(f"Failed to load environment: {e}")
        return

    obs, info = env.reset()
    print(f"Initial RAM State: {info}")
    
    # Action: Hold 'B' (Gas) - usually index 0 in retro SNES
    # Order: B, Y, SELECT, START, UP, DOWN, LEFT, RIGHT, A, X, L, R
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1 
    
    print("\nHolding Gas for 300 steps...")
    for i in range(300):
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 10 == 0:
            print(f"Step {i}: X={info.get('x')}, Y={info.get('y')}, Angle={info.get('angle')}, Status={info.get('status')}")
    
    final_info = info
    print(f"\nFinal RAM State: {final_info}")
    
    # Check for movement
    if final_info['x'] != 0 or final_info['y'] != 0:
        print("\nSUCCESS: RAM values are changing. Coordinates are active.")
    else:
        print("\nWARNING: Coordinates did not change. The kart might be stuck or the addresses might be incorrect for this ROM.")

    env.close()

if __name__ == "__main__":
    verify()
