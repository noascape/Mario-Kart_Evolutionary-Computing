import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def save_and_verify():
    print("Running until step 2500, then saving and verifying movement...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    # Reach 2500
    for i in range(2501):
        action = np.zeros(12, dtype=np.int8)
        if i % 40 < 10: action[3] = 1 # START
        if 20 <= i % 40 < 30: action[8] = 1 # A
        obs, _, _, _, _ = env.step(action)
        if i == 2500:
            print(f"Step 2500 reached. Saving state...")
            state_data = env.unwrapped.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            cv2.imwrite("recovered_start_verify.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    print("State saved. Now holding B for 300 steps to verify movement...")
    for i in range(300):
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # B
        obs, _, _, _, _ = env.step(action)
        ram = env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        if i % 50 == 0:
            print(f"Verify Step {i}: X={x}, Y={y}")
            cv2.imwrite(f"verify_move_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    save_and_verify()
