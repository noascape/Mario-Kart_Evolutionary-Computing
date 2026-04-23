import stable_retro as retro
import os
import cv2
import numpy as np
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def final_reconstruction():
    print("ULTIMATE RECONSTRUCTION START...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()
    
    def press(button, wait=200):
        action = np.zeros(12, dtype=np.int8)
        mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
        action[mapping[button]] = 1
        for _ in range(10): env.step(action)
        for _ in range(wait): env.step(np.zeros(12, dtype=np.int8))

    # Patient Navigation
    print("Skipping intro...")
    for _ in range(1500): env.step(np.zeros(12, dtype=np.int8))
    press("START", 500)
    press("START", 500)
    print("Selecting GP/50cc/Mario/Cup...")
    press("A", 500) # GP
    press("A", 500) # 1P
    press("A", 500) # 50cc
    press("A", 500) # Mario
    press("A", 500) # Mushroom Cup
    
    print("Scanning for track image signature (Mean ~91)...")
    for i in range(10000):
        obs, _, _, _, _ = env.step(np.zeros(12, dtype=np.int8))
        mean = np.mean(obs)
        
        if i % 500 == 0:
            print(f"  Frame {i}, Mean: {mean}")
            
        if 91.0 < mean < 92.0:
            print(f"MATCH FOUND! Frame {i}, Mean: {mean}")
            # Verify it's actually the track (size check)
            frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
            fname = "recovered_start_verify.png"
            cv2.imwrite(fname, frame_bgr)
            if os.path.getsize(fname) > 30000:
                print("Track confirmed! Saving state.")
                state_data = env.unwrapped.em.get_state()
                state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
                with gzip.open(state_path, 'wb') as f:
                    f.write(state_data)
                cv2.imwrite('actual_start_line.png', frame_bgr)
                break
    
    env.close()

if __name__ == "__main__":
    final_reconstruction()
