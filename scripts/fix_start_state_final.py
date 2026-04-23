import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def fix_start_state():
    print("Fixing start state: Navigating until Race Start...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press(buttons, duration=15, wait=100):
        for _ in range(duration):
            action = np.zeros(12, dtype=np.int8)
            mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
            for b in buttons: action[mapping[b]] = 1
            env.step(action)
        for _ in range(wait):
            env.step(np.zeros(12, dtype=np.int8))

    print("Spamming START/A to skip intros...")
    for _ in range(5):
        press(["START"], 20, 200)
        press(["A"], 20, 200)

    print("Selecting GP, 50cc, Mario, Mushroom Cup...")
    press(["A"], 20, 300) # Mario GP
    press(["A"], 20, 300) # 50cc
    press(["A"], 20, 300) # Mario
    press(["A"], 20, 300) # Mushroom Cup
    
    print("Race selection complete. Waiting for Lakitu countdown...")
    
    # Now we wait until Lap == 128 AND movement detected
    # We'll also hold B (Gas) to detect when we can actually move
    for i in range(2000):
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # Hold Gas
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        lap = ram[0x10C1 - 0x0000]
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        
        # In SMK, Mario Circuit 1 start line X is usually around 1000+
        if lap == 128 and x > 500:
            print(f"RACE START DETECTED at step {i}! Lap={lap}, X={x}, Y={y}")
            
            # Save the state
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            
            cv2.imwrite("RECOVERED_start_line.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Successfully saved {state_path}")
            break
        
        if i % 100 == 0:
            print(f"Waiting... Step {i}, Lap={lap}, X={x}, Y={y}")
            cv2.imwrite(f"wait_step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    fix_start_state()
