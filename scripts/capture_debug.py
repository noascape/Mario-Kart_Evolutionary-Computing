import os
import sys
import cv2
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    import stable_retro as retro
except ImportError:
    import retro

from src.env.mario_kart_wrapper import MarioKartWrapper

custom_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration'))
retro.data.add_custom_integration(custom_path)

def capture_debug_frames():
    print("Capturing debug frames...")
    state_path = os.path.abspath(os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state'))
    try:
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=state_path, 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        env = MarioKartWrapper(inner_env)
    except Exception as e:
        print(f"Failed to load environment: {e}")
        return

    obs, info = env.reset()
    cv2.imwrite("debug_start_frame.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
    print(f"Step 0: X={info.get('x')}, Y={info.get('y')}, CP={info.get('checkpoint')}, Lap={info.get('lap')}")
    
    # Run for 200 steps
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1 # Gas
    
    for i in range(1, 201):
        obs, reward, terminated, truncated, info = env.step(action)
        if i % 50 == 0:
            cv2.imwrite(f"debug_frame_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Step {i}: X={info.get('x')}, Y={info.get('y')}, CP={info.get('checkpoint')}, Lap={info.get('lap')}")
            
    env.close()

if __name__ == "__main__":
    capture_debug_frames()
