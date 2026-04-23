import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def verify_start():
    print("Verifying the newly saved 'start_race.state'...")
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    
    # Load and reset
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=os.path.abspath(state_path), 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    obs, info = env.reset()
    cv2.imwrite("actual_start_line_TEST.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
    
    print(f"{'Step':>6} | {'X':>6} | {'Y':>6} | {'Lap':>6} | {'Status':>6}")
    
    for i in range(1001):
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # B
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        status = ram[0x10AE]
        
        if i % 100 == 0:
            print(f"{i:6} | {x:6} | {y:6} | {lap:6} | {status:6}")
            cv2.imwrite(f"verify_test_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            
    env.close()

if __name__ == "__main__":
    verify_start()
