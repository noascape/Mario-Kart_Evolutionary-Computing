import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def aggressive_reach_race():
    print("Aggressive race reach attempt...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    # Step 1: Wait for Title Screen (Wait long enough for the whole intro demo)
    print("Waiting for title screen (2500 steps)...")
    for _ in range(2500): env.step(np.zeros(12, dtype=np.int8))
    
    def press_and_wait(button, duration=20, wait=300):
        action = np.zeros(12, dtype=np.int8)
        mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
        action[mapping[button]] = 1
        for _ in range(duration): env.step(action)
        for _ in range(wait): env.step(np.zeros(12, dtype=np.int8))

    print("Spamming START to get to Main Menu...")
    press_and_wait("START")
    press_and_wait("START")
    
    print("Selecting Mario GP (A)...")
    press_and_wait("A")
    
    print("Selecting 50cc (A)...")
    press_and_wait("A")
    
    print("Selecting Mario (A)...")
    press_and_wait("A")
    
    print("Selecting Mushroom Cup (A)...")
    press_and_wait("A")
    
    print("Waiting for race start (800 steps)...")
    for i in range(1500):
        # Hold Gas (B)
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x88] + (ram[0x89] << 8)
        y = ram[0x8C] + (ram[0x8D] << 8)
        
        if x > 500 and y > 500:
            print(f"RACE DETECTED at step {i}! X={x}, Y={y}")
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("SUCCESS_race_start.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
        
        if i % 100 == 0:
            print(f"Race Wait Step {i}... X={x}, Y={y}")
            cv2.imwrite(f"race_wait_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    aggressive_reach_race()
