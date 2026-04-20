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

def capture_start():
    print("Loading environment with start_race.state...")
    try:
        state_path = os.path.abspath(os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state'))
        env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=state_path, 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        obs, info = env.reset()
        
        output_path = "actual_start_line.png"
        cv2.imwrite(output_path, cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
        print(f"Screenshot of loaded state saved to {output_path}")
        
        # Also print RAM values at this exact moment
        # We need to wrap it to use our get_val logic
        wrapped_env = MarioKartWrapper(env)
        # We don't call reset again, just look at what info we can get or trigger a step
        _, _, _, _, wrap_info = wrapped_env.step(np.zeros(12, dtype=np.int8))
        print(f"RAM at start line: {wrap_info}")
        
        env.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capture_start()
