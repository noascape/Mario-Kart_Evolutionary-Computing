import stable_retro as retro
import os
import cv2
import numpy as np
import sys

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def reconstruct():
    print("Reconstructing boot sequence...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    os.makedirs('boot_debug', exist_ok=True)
    
    for i in range(6001):
        action = np.zeros(12, dtype=np.int8)
        if i % 40 < 10: action[3] = 1 # START
        if 20 <= i % 40 < 30: action[8] = 1 # A
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 250 == 0:
            fname = f"boot_debug/frame_{i}.png"
            cv2.imwrite(fname, cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Saved {fname}")

    env.close()

if __name__ == "__main__":
    reconstruct()
