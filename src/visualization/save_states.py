import os
import cv2
import numpy as np
import gzip
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

def save_states():
    print("Capturing states for manual verification...")
    custom_path = os.path.join(project_root, 'src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    inner_env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        render_mode='rgb_array', 
        inttype=retro.data.Integrations.CONTRIB_ONLY
    )
    
    inner_env.reset()
    
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    os.makedirs('nav_debug', exist_ok=True)

    for i in range(5001):
        action = np.zeros(len(buttons), dtype=np.int8)
        if i % 40 < 10: action[3] = 1 # START
        if 15 <= i % 40 < 25: action[8] = 1 # A
        
        obs, _, _, _, _ = inner_env.step(action)
        
        if i % 500 == 0:
            fname = f"nav_debug/step_{i}.png"
            cv2.imwrite(fname, cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            state_data = inner_env.em.get_state()
            with gzip.open(f"nav_debug/step_{i}.state", 'wb') as f:
                f.write(state_data)
            print(f"Saved step {i} to {fname}")

    inner_env.close()

if __name__ == "__main__":
    save_states()
