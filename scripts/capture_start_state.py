import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip
import time

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def capture():
    print("--- Super Mario Kart: Start State Capture ---")
    print("Booting from cold start...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press(button, wait=120):
        print(f"  Action: Pressing {button}...")
        action = np.zeros(12, dtype=np.int8)
        mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
        action[mapping[button]] = 1
        # Hold for 10 frames
        for _ in range(10): env.step(action)
        # Wait for menu animation
        for _ in range(wait): env.step(np.zeros(12, dtype=np.int8))

    # 1. Skip Intro and Spam Menus
    print("Step 1: Spamming START and A to navigate menus...")
    # Wait for initial boot
    for _ in range(300): env.step(np.zeros(12, dtype=np.int8))
    
    for i in range(4000):
        action = np.zeros(12, dtype=np.int8)
        # Intense spamming pattern
        if i % 30 < 10: action[3] = 1 # START
        if 15 <= i % 30 < 25: action[8] = 1 # A
        
        obs, _, _, _, _ = env.step(action)
        
        if i % 500 == 0:
            ram = env.get_ram()
            x = ram[0x0088] + (ram[0x0089] << 8)
            y = ram[0x008C] + (ram[0x008D] << 8)
            print(f"  Spamming... Frame {i}, X={x}, Y={y}")

    print("Step 2: Waiting for Lakitu countdown and track positioning...")
    
    captured = False
    # Run for up to 5000 frames to find the race
    for i in range(5000):
        # Hold Gas (B) during search to verify movement
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # B
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        
        # Real Mario Circuit 1 Start coordinates are usually X ~ 1024, Y ~ 1824
        if x > 500 and lap == 128:
            print(f"SUCCESS! Race detected at frame {i}.")
            print(f"Final Coordinates: X={x}, Y={y}, Lap={lap}")
            
            # Capture the state
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            
            # Save visual proof
            cv2.imwrite("actual_start_line.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Saved state to: {state_path}")
            print("Visual proof saved to: actual_start_line.png")
            captured = True
            break
            
        if i % 100 == 0:
            print(f"  Waiting... Frame {i}, X={x}, Y={y}")

    env.close()
    if not captured:
        print("ERROR: Failed to reach the race. Check your ROM version or menu timings.")

if __name__ == "__main__":
    capture()
