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

def visual_verify():
    print("Initializing environment for visual verification...")
    try:
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=os.path.abspath(os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')), 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        env = MarioKartWrapper(inner_env)
    except Exception as e:
        print(f"Failed to load environment: {e}")
        return

    obs, info = env.reset()
    
    # Action: Hold 'B' (Gas)
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1 
    
    print("\nHolding Gas and capturing frames...")
    for i in range(500):
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 50 == 0:
            fname = f"verify_step_{i}.png"
            cv2.imwrite(fname, cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            print(f"Step {i}: X={info.get('x')}, Y={info.get('y')}, Angle={info.get('angle')} -> Saved {fname}")
    
    env.close()

if __name__ == "__main__":
    visual_verify()
