import stable_retro as retro
import os
import cv2
import numpy as np
import time
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def navigate():
    # Start from cold boot
    print("Booting Super Mario Kart...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press(buttons, duration=20, wait=200):
        for _ in range(duration):
            action = np.zeros(12, dtype=np.int8)
            for b in buttons:
                mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
                action[mapping[b]] = 1
            env.step(action)
        # Wait more
        for _ in range(wait):
            env.step(np.zeros(12, dtype=np.int8))

    print("Navigating menus...")
    # Skip intros - Mario Kart intro is VERY long
    for _ in range(800): env.step(np.zeros(12, dtype=np.int8))
    print("Pressing START to skip intro...")
    press(["START"], 50, 400)
    
    # Try another START just in case
    press(["START"], 50, 400)
    
    # Menu Selection:
    # Mario GP
    print("Selecting Mario GP...")
    press(["A"], 50, 400)
    
    # 50cc
    print("Selecting 50cc...")
    press(["A"], 50, 400)
    
    # Mario (default)
    print("Selecting Mario...")
    press(["A"], 50, 400)
    # Mushroom Cup (default)
    print("Selecting Mushroom Cup...")
    press(["A"], 50, 400)
    cv2.imwrite('debug_menu_cup.png', cv2.cvtColor(env.render(), cv2.COLOR_RGB2BGR))

    # NEW: Wait a short bit and capture BEFORE movement
    print("Capturing fresh start line state...")
    for _ in range(100): env.step(np.zeros(12, dtype=np.int8))

    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    state_data = env.unwrapped.em.get_state()
    with gzip.open(state_path, 'wb') as f:
        f.write(state_data)
    print(f"Saved {state_path}")

    frame_bgr = cv2.cvtColor(env.render(), cv2.COLOR_RGB2BGR)
    cv2.imwrite('reconstructed_start.png', frame_bgr)

    env.close()


if __name__ == "__main__":
    navigate()
