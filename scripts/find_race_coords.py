import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def find_race():
    print("Finding race start by track coordinates...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    # Increase loop to 15,000 to be absolutely sure
    for i in range(15000):
        action = np.zeros(12, dtype=np.int8)
        # Spam pattern
        if i % 40 < 10: action[3] = 1 # START
        if 15 <= i % 40 < 25: action[8] = 1 # A
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        
        # Real Mario Circuit 1 Start: X ~ 1000+, Y ~ 1000+
        if x > 500 and y > 500 and lap == 128:
            print(f"!!! RACE DETECTED !!! Step={i}, X={x}, Y={y}, Lap={lap}")
            # Save state
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("ACTUAL_RACE_START.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
            
        if i % 1000 == 0:
            print(f"Step {i}: X={x}, Y={y}, Lap={lap}")

    env.close()

if __name__ == "__main__":
    find_race()
