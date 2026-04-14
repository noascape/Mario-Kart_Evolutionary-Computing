import os
import cv2
import numpy as np
from src.env.mario_kart_wrapper import MarioKartWrapper

try:
    import stable_retro as retro
except ImportError:
    import retro

def record_video():
    print("Initializing environment...")
    inner_env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE, render_mode='rgb_array')
    env = MarioKartWrapper(inner_env)
    
    print("Resetting environment...")
    env.reset()
    
    output_path = 'Gameplay/race_start.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 60.0, (256, 224))
    
    buttons = ['B', 'Y', 'SELECT', 'START', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'A', 'X', 'L', 'R']
    
    def multi_press(names, times=3, duration=20, wait_between=60):
        """Presses a set of buttons multiple times with delays."""
        for i in range(times):
            print(f"  Action: Pressing {names} (Attempt {i+1})...")
            action = np.zeros(len(buttons), dtype=np.int8)
            for name in names:
                action[buttons.index(name)] = 1
            
            for _ in range(duration):
                obs, _, _, _, _ = env.step(action)
                out.write(cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
                
            # Release
            action = np.zeros(len(buttons), dtype=np.int8)
            for _ in range(wait_between):
                obs, _, _, _, _ = env.step(action)
                out.write(cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    def wait(seconds):
        print(f"  Waiting for {seconds} seconds...")
        for _ in range(int(60 * seconds)):
            obs, _, _, _, _ = env.step(np.zeros(len(buttons), dtype=np.int8))
            out.write(cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    # 1. Initial Wait (10s)
    print("Step 1: Waiting for title screen...")
    wait(10)
    
    # 2. Start screen -> Main Menu
    print("Step 2: Title -> Menu (START + B)...")
    multi_press(['START', 'B'])
    wait(5)
    
    # 3. Select 'Mario Kart GP'
    print("Step 3: Selecting Mario Kart GP (B)...")
    multi_press(['B'])
    wait(5)
    
    # 4. Select '1P Game'
    print("Step 4: Selecting 1P Game (B)...")
    multi_press(['B'])
    wait(5)
    
    # 5. Select '50cc'
    print("Step 5: Selecting 50cc (B)...")
    multi_press(['B'])
    wait(8) # Extra wait for character screen load
    
    # 6. Character Selection (Try B then A)
    print("Step 6: Selecting Character Mario (B then A)...")
    multi_press(['B'])
    wait(2)
    multi_press(['A'])
    wait(8) # Extra wait for cup screen load
    
    # 7. Cup Selection (Try B then A)
    print("Step 7: Selecting Mushroom Cup (B then A)...")
    multi_press(['B'])
    wait(2)
    multi_press(['A'])
    
    # 8. Final Wait for Track Flyover and Race Start (30s)
    print("Step 8: Final capture (Lakitu countdown)...")
    wait(30)
    
    out.release()
    env.close()
    print(f"Video saved as {output_path}")

if __name__ == "__main__":
    record_video()
