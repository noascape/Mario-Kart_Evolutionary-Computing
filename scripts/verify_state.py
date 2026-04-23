import stable_retro as retro
import os
import cv2
import numpy as np

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def verify():
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    print(f"Loading state: {state_path}")
    
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=state_path, 
        inttype=retro.data.Integrations.CONTRIB_ONLY, 
        render_mode='rgb_array'
    )
    
    obs, info = env.reset()
    frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
    cv2.imwrite('actual_start_line.png', frame_bgr)
    print("Saved 'actual_start_line.png'. Please check if this is the start line or a menu.")
    
    # Check RAM values at start
    ram = env.get_ram()
    # Check x, y, lap
    x = ram[0x0088] + (ram[0x0089] << 8)
    y = ram[0x008C] + (ram[0x008D] << 8)
    lap = ram[0x10C1]
    print(f"RAM at Start - X: {x}, Y: {y}, Lap: {lap}")
    
    env.close()

if __name__ == "__main__":
    verify()
