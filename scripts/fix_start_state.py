import stable_retro as retro
import os
import cv2
import numpy as np
import sys

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def create_state():
    # Load from none to start from boot or from existing if we want to skip menus
    # Let's try to load the existing one and just advance it until movement
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=state_path, 
        inttype=retro.data.Integrations.CONTRIB_ONLY
    )
    
    env.reset()
    print("Advancing until movement detected...")
    
    last_y = None
    for i in range(500):
        # Hold Gas (B)
        action = np.zeros(12, dtype=np.int8)
        action[0] = 1 
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        y = ram[0x008C] + (ram[0x008D] << 8)
        
        if last_y is not None and y != last_y:
            print(f"Movement detected at step {i}! Y changed from {last_y} to {y}")
            # Save this state
            # In stable-retro, we can use env.unwrapped.em.get_state()
            # but usually, we just save the bytes from a state file or similar.
            # However, the easiest way is to use the state property if available
            # or the underlying emulator's state.
            try:
                import gzip
                state_data = env.unwrapped.em.get_state()
                with gzip.open(state_path, 'wb') as f:
                    f.write(state_data)
                print(f"Updated {state_path} with moving state (gzipped).")
            except AttributeError:
                print("Could not find em.get_state(), attempting alternative...")
                # Retro sometimes exposes it via the core
                state_data = env.em.get_state()
                with gzip.open(state_path, 'wb') as f:
                    f.write(state_data)

            # Save a preview
            frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
            cv2.imwrite('new_start_preview.png', frame_bgr)
            break
        last_y = y
        
    env.close()

if __name__ == "__main__":
    create_state()
