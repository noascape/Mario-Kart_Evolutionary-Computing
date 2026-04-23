import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def reach_race():
    print("Attempting to reach the race by spamming A...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    for i in range(5000):
        action = np.zeros(12, dtype=np.int8)
        if i % 10 < 5:
            action[8] = 1 # Spam A
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x88] + (ram[0x89] << 8)
        y = ram[0x8C] + (ram[0x8D] << 8)
        
        if x > 500 and y > 500:
            print(f"Race detected at step {i}! X={x}, Y={y}")
            # Save the state
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            print(f"Saved state to {state_path}")
            
            cv2.imwrite("actual_race_start.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            
            # Print RAM values at this point
            cp_s = ram[0x10C0 - 0x0000] # Wait, WRAM is 0x7E0000
            cp_u = ram[0x1020 - 0x0000]
            cp_r = ram[0x10DC - 0x0000]
            lap = ram[0x10C1 - 0x0000]
            print(f"RAM: Lap={lap}, CP_User={cp_u}, CP_Search={cp_s}, CP_Remote={cp_r}")
            break
            
        if i % 500 == 0:
            print(f"Step {i}... X={x}, Y={y}")
            cv2.imwrite(f"reconstruct_step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    reach_race()
