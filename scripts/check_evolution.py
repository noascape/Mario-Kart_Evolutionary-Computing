import os
import sys
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

def check_evolution():
    print("Checking evolution of RAM values...")
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
    
    def get_val(addr):
        ram = env.unwrapped.get_ram()
        wram_addr = addr - 0x7E0000
        return ram[wram_addr]

    print(f"{'Step':>5} | {'Lap':>5} | {'CP':>5} | {'TotalCP':>7} | {'RemoteCP':>8} | {'RemoteTCP':>9} | {'X':>5} | {'Y':>5}")
    print("-" * 75)
    
    # Action: Hold 'B' (Gas)
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1 
    
    for i in range(1001):
        obs, reward, terminated, truncated, info = env.step(action)
        
        if i % 100 == 0:
            lap = get_val(0x7E10C1)
            cp = get_val(0x7E1020)
            tcp = get_val(0x7E1162)
            remote_cp = get_val(0x7E10DC)
            remote_tcp = get_val(0x7E0148)
            x = info.get('x')
            y = info.get('y')
            
            print(f"{i:5} | {lap:5} | {cp:5} | {tcp:7} | {remote_cp:8} | {remote_tcp:9} | {x:5} | {y:5}")
            
        if terminated or truncated:
            print(f"Terminated at step {i}")
            break

    env.close()

if __name__ == "__main__":
    check_evolution()
