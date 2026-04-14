import os
import cv2
import numpy as np
from src.env.mario_kart_wrapper import MarioKartWrapper

try:
    import stable_retro as retro
except ImportError:
    import retro

def capture():
    print("Initializing environment...")
    # Use render_mode='rgb_array' to get the image data
    inner_env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE, render_mode='rgb_array')
    env = MarioKartWrapper(inner_env)
    
    print("Resetting environment...")
    obs, info = env.reset()
    
    # The observation is already the image (RGB)
    # OpenCV uses BGR, so we convert
    frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
    
    output_path = "debug_frame.png"
    cv2.imwrite(output_path, frame_bgr)
    print(f"Screenshot saved to {output_path}")
    
    env.close()

if __name__ == "__main__":
    capture()
