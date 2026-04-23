import stable_retro as retro
import os
import cv2
import numpy as np
import sys
import gzip

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def verify_and_move():
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    print(f"Testing newly downloaded state: {state_path}")
    
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=os.path.abspath(state_path), 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    obs, info = env.reset()
    
    print(f"Step | X | Y | Lap | CP | Surface")
    print("-" * 40)
    
    for i in range(200):
        # Hold Gas (B)
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 # B
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        x = ram[136] + (ram[137] << 8)
        y = ram[140] + (ram[141] << 8)
        lap = ram[4289]
        cp = ram[4316]
        surface = ram[4270]
        
        if i % 40 == 0:
            print(f"{i:4} | {x:4} | {y:4} | {lap:3} | {cp:2} | {surface:3}")
            cv2.imwrite(f"verify_repo_step_{i}.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))

    env.close()

if __name__ == "__main__":
    verify_and_move()
