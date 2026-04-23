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

def debug_full_boot():
    print("Booting and capturing frames to see where it gets stuck...")
    env = retro.make(game='SuperMarioKart-Snes-v0', state=None, inttype=retro.data.Integrations.CONTRIB_ONLY, render_mode='rgb_array')
    env.reset()
    
    # We'll spam A and START while capturing
    for i in range(5001):
        action = np.zeros(12, dtype=np.int8)
        if i % 20 < 10:
            action[8] = 1 # A
            action[3] = 1 # START
            
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 250 == 0:
            cv2.imwrite(f"boot_step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            ram = env.get_ram()
            x = ram[0x88] + (ram[0x89] << 8)
            y = ram[0x8C] + (ram[0x8D] << 8)
            lap = ram[0x10C1]
            print(f"Step {i}: Lap={lap}, X={x}, Y={y}")
            
    env.close()

if __name__ == "__main__":
    debug_full_boot()
