import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def navigate():
    print("Final attempt at navigation...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press_A(wait_steps):
        print(f"Pressing A, waiting {wait_steps} steps...")
        action = np.zeros(12, dtype=np.int8)
        action[8] = 1 # A
        for _ in range(10): env.step(action)
        for _ in range(wait_steps): env.step(np.zeros(12, dtype=np.int8))

    # Intro
    print("Waiting 1000 steps for intro...")
    for _ in range(1000): env.step(np.zeros(12, dtype=np.int8))
    
    # Title Screen
    press_A(200)
    # Mode Selection (Mario GP)
    press_A(200)
    # CC Selection (50cc)
    press_A(200)
    # Char Selection (Mario)
    press_A(200)
    # Cup Selection (Mushroom)
    press_A(500)
    
    print("Wait for Race...")
    for i in range(1500):
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # Gas
        obs, reward, terminated, truncated, info = env.step(action)
        ram = env.get_ram()
        x = ram[0x88] + (ram[0x89] << 8)
        y = ram[0x8C] + (ram[0x8D] << 8)
        if x > 500 and y > 500:
            print(f"SUCCESS! Race at step {i}, X={x}, Y={y}")
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("FINAL_SUCCESS.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
        if i % 100 == 0:
            print(f"Step {i}, X={x}, Y={y}")
            cv2.imwrite(f"final_wait_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    navigate()
