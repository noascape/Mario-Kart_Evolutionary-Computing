import os
import cv2
import numpy as np
import gzip
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

def record_navigation():
    print("Initializing environment for navigation recording...")
    custom_path = os.path.join(project_root, 'src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    # We use State.NONE to start from cold boot
    inner_env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        render_mode='rgb_array', 
        inttype=retro.data.Integrations.CONTRIB_ONLY
    )
    
    obs, info = inner_env.reset()
    
    # Video setup
    video_path = 'navigation_verify.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # SMK resolution is usually 256x224, but let's get it from the obs
    height, width, layers = obs.shape
    video = cv2.VideoWriter(video_path, fourcc, 60.0, (width, height))
    
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    def step_and_record(action, count=1):
        nonlocal obs
        for _ in range(count):
            obs, reward, terminated, truncated, info = inner_env.step(action)
            frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
            video.write(frame_bgr)
        return obs, info

    def press(button, duration=20, wait=300):
        print(f"Pressing {button}...")
        action = np.zeros(len(buttons), dtype=np.int8)
        action[buttons.index(button)] = 1
        step_and_record(action, duration)
        step_and_record(np.zeros(len(buttons), dtype=np.int8), wait)

    print("Step 1: Waiting for Intro...")
    step_and_record(np.zeros(len(buttons), dtype=np.int8), 600)
    
    print("Step 2: Spamming START and A to navigate menus...")
    # Spam for 2000 steps to get through all selections
    for i in range(2000):
        action = np.zeros(len(buttons), dtype=np.int8)
        # Alternate START and A
        if i % 40 < 10: action[3] = 1 # START
        if 20 <= i % 40 < 30: action[8] = 1 # A
        step_and_record(action, 1)

    print("Step 3: Waiting for Race Start (Watching X/Y)...")
    race_detected = False
    for i in range(5000):
        # Hold Gas (B)
        action = np.zeros(len(buttons), dtype=np.int8)
        action[0] = 1 # B
        
        obs, info = step_and_record(action, 1)
        
        ram = inner_env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        
        # Real Mario Circuit 1 Start: X is usually ~1024, Y is ~1824
        # We look for a jump into large coordinate space
        if x > 500 and y > 500 and lap == 128:
            print(f"RACE DETECTED! Step={i}, X={x}, Y={y}, Lap={lap}")
            race_detected = True
            state_data = inner_env.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            print(f"State saved to {state_path}")
            step_and_record(action, 180) # Record 3s of race
            break
            
        if i % 250 == 0:
            print(f"  Wait Frame {i}, X: {x}, Y: {y}, Lap: {lap}")

    video.release()
    inner_env.close()
    print(f"Navigation complete. Video saved to {video_path}")

if __name__ == "__main__":
    record_navigation()
