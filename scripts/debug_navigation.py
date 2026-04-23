import stable_retro as retro
import os
import cv2
import numpy as np
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def debug_nav():
    print("--- Super Mario Kart: Navigation Debug ---")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    os.makedirs('nav_debug', exist_ok=True)

    for i in range(5001):
        action = np.zeros(12, dtype=np.int8)
        # Spam pattern
        if i % 40 < 10: action[3] = 1 # START
        if 20 <= i % 40 < 30: action[8] = 1 # A
        
        obs, _, _, _, _ = env.step(action)
        
        if i % 100 == 0:
            ram = env.get_ram()
            x = ram[0x0088] + (ram[0x0089] << 8)
            y = ram[0x008C] + (ram[0x008D] << 8)
            lap = ram[0x10C1]
            print(f"Frame {i}: X={x}, Y={y}, Lap={lap}")
            cv2.imwrite(f"nav_debug/frame_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    debug_nav()
