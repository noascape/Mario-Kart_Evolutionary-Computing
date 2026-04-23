import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def find_race_manually():
    print("Finding race manually: Cold boot + slow steps...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    # Wait for Title Screen (The intro is really long)
    print("Waiting for title (3000 steps)...")
    for _ in range(3000): env.step(np.zeros(12, dtype=np.int8))
    
    def press_A(wait=600):
        action = np.zeros(12, dtype=np.int8)
        action[8] = 1
        for _ in range(20): env.step(action)
        for _ in range(wait): env.step(np.zeros(12, dtype=np.int8))

    print("Pressing A (Title Screen)...")
    press_A()
    print("Pressing A (Mario GP)...")
    press_A()
    print("Pressing A (50cc)...")
    press_A()
    print("Pressing A (Mario)...")
    press_A()
    print("Pressing A (Mushroom Cup)...")
    press_A(1000) # Wait longer for loading
    
    print("Now waiting for coordinates to change...")
    for i in range(2000):
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # Gas
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x88] + (ram[0x89] << 8)
        y = ram[0x8C] + (ram[0x8D] << 8)
        lap = ram[0x10C1]
        
        if x > 500 and y > 500:
            print(f"RACE DETECTED! Step={i}, X={x}, Y={y}, Lap={lap}")
            # Save this state
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("FIXED_race_start.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
            
        if i % 100 == 0:
            print(f"Wait Step {i}: X={x}, Y={y}, Lap={lap}")
            cv2.imwrite(f"reconstruct_wait_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    find_race_manually()
