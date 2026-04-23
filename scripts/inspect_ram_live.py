import stable_retro as retro
import os
import cv2
import numpy as np
import sys

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def inspect_live():
    print("Cold booting for live RAM inspection...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    print(f"{'Step':>6} | {'Lap':>4} | {'X':>6} | {'Y':>6} | {'Status':>6}")
    
    for i in range(10000):
        action = np.zeros(12, dtype=np.int8)
        # Intense spamming
        if i % 20 < 10: action[3] = 1 # START
        if 5 <= i % 20 < 15: action[8] = 1 # A
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        status = ram[0x10AE]
        
        if x > 500 and y > 500 and lap == 128:
            print(f"!!! RACE DETECTED at step {i} !!!")
            cv2.imwrite("detected_race.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
            
        if i % 200 == 0:
            print(f"{i:6} | {lap:4} | {x:6} | {y:6} | {status:6}")

    env.close()

if __name__ == "__main__":
    inspect_live()
