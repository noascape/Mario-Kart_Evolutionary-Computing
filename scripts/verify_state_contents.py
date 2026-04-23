import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def verify_state():
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    print(f"Inspecting: {state_path}")
    
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=os.path.abspath(state_path), 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    obs, info = env.reset()
    
    ram = env.get_ram()
    # Using decimal addresses from the new data.json to be safe
    # x: 136, y: 140, lap: 4289, cp: 4316, tcp: 328, surface: 4270
    x = ram[136] + (ram[137] << 8)
    y = ram[140] + (ram[141] << 8)
    lap = ram[4289]
    cp = ram[4316]
    tcp = ram[328]
    surface = ram[4270]
    
    print(f"Values at reset (Using new Repository addresses):")
    print(f"  X (kart1_X): {x}")
    print(f"  Y (kart1_Y): {y}")
    print(f"  Lap (lap): {lap}")
    print(f"  Checkpoint (current_checkpoint): {cp}")
    print(f"  Total Checkpoints (totalCheckpoints): {tcp}")
    print(f"  Surface (surface): {surface}")
    
    cv2.imwrite("current_state_reset.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
    env.close()

if __name__ == "__main__":
    verify_state()
