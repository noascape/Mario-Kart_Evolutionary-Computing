import os
import sys
import cv2
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

def debug_gameplay():
    env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE, inttype=retro.data.Integrations.CONTRIB_ONLY, render_mode='rgb_array')
    obs, info = env.reset()
    
    # Take screenshot at step 0
    cv2.imwrite("step_0.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
    
    # Hold gas (B)
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1
    
    for i in range(120): # Run longer to be sure
        obs, reward, terminated, truncated, info = env.step(action)
        if i % 30 == 0:
            cv2.imwrite(f"step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Saved step_{i}.png")
            
    env.close()

if __name__ == "__main__":
    debug_gameplay()
