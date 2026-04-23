import os
import cv2
import numpy as np
import gzip
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

def record_navigation():
    print("Initializing environment (Cold Boot)...")
    custom_path = os.path.join(project_root, 'src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    inner_env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        render_mode='rgb_array', 
        inttype=retro.data.Integrations.CONTRIB_ONLY
    )
    
    obs, info = inner_env.reset()
    
    video_path = 'navigation_verify.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    height, width, layers = obs.shape
    video = cv2.VideoWriter(video_path, fourcc, 60.0, (width, height))
    
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    print("Spamming START and A to find the race...")
    race_detected = False
    for i in range(10000):
        action = np.zeros(len(buttons), dtype=np.int8)
        # Spam pattern
        if i % 40 < 10: action[3] = 1 # START
        if 15 <= i % 40 < 25: action[8] = 1 # A
        
        obs, reward, terminated, truncated, info = inner_env.step(action)
        
        # Record every 2nd frame to keep video size sane but 30fps-ish
        if i % 2 == 0:
            frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
            video.write(frame_bgr)
        
        ram = inner_env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        lap = ram[0x10C1]
        
        if x > 500 and y > 500 and lap == 128:
            print(f"RACE START DETECTED at step {i}! X={x}, Y={y}, Lap={lap}")
            race_detected = True
            # Save state
            state_data = inner_env.em.get_state()
            state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
            with gzip.open(state_path, 'wb') as f:
                f.write(state_data)
            print(f"State saved to {state_path}")
            
            # Record a bit more
            for _ in range(120):
                action = np.zeros(len(buttons), dtype=np.int8)
                action[0] = 1 # Hold B
                obs, _, _, _, _ = inner_env.step(action)
                video.write(cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            break
            
        if i % 1000 == 0:
            print(f"  Step {i}, X: {x}, Y: {y}, Lap: {lap}")

    video.release()
    inner_env.close()
    if not race_detected:
        print("Failed to detect race start.")
    else:
        print(f"Navigation complete. Video saved to {video_path}")

if __name__ == "__main__":
    record_navigation()
