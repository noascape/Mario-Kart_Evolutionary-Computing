import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def find_race_by_coords():
    print("Searching for race start by track coordinates...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press(button, wait=60):
        action = np.zeros(12, dtype=np.int8)
        mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
        action[mapping[button]] = 1
        for _ in range(10): env.step(action)
        for _ in range(wait): env.step(np.zeros(12, dtype=np.int8))

    # Try to skip everything by spamming START and A
    print("Spamming START and A for 10000 steps...")
    for i in range(10000):
        action = np.zeros(12, dtype=np.int8)
        if i % 30 < 10: action[3] = 1 # START
        if i % 30 >= 10 and i % 30 < 20: action[8] = 1 # A
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x88] + (ram[0x89] << 8)
        y = ram[0x8C] + (ram[0x8D] << 8)
        lap = ram[0x10C1]
        
        # Look for coordinates in the racing range
        if x > 500 and y > 500:
            print(f"RACE DETECTED! Step={i}, X={x}, Y={y}, Lap={lap}")
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("FOUND_race_start.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
            
        if i % 1000 == 0:
            print(f"Searching... Step {i}, X={x}, Y={y}, Lap={lap}")
            cv2.imwrite(f"search_step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    find_race_by_coords()
