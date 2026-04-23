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

def verify():
    custom_path = os.path.join(project_root, 'src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    # Test step 2500
    state_to_test = "nav_debug/step_2500.state"
    print(f"Testing state: {state_to_test}")
    
    inner_env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=os.path.abspath(state_to_test), 
        render_mode='rgb_array', 
        inttype=retro.data.Integrations.CONTRIB_ONLY
    )
    
    obs, info = inner_env.reset()
    video_path = 'recovery_verify.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    height, width, layers = obs.shape
    video = cv2.VideoWriter(video_path, fourcc, 60.0, (width, height))
    
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    print("Holding Gas (B)...")
    for i in range(300):
        action = np.zeros(len(buttons), dtype=np.int8)
        action[0] = 1 # B
        obs, reward, terminated, truncated, info = inner_env.step(action)
        
        ram = inner_env.get_ram()
        x = ram[0x0088] + (ram[0x0089] << 8)
        y = ram[0x008C] + (ram[0x008D] << 8)
        
        video.write(cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
        if i % 50 == 0:
            print(f"Step {i}: X={x}, Y={y}")
            
    video.release()
    inner_env.close()
    print(f"Verify complete. Saved to {video_path}")

if __name__ == "__main__":
    verify()
