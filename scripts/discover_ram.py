import stable_retro as retro
import os
import cv2
import numpy as np
import sys

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
custom_path = os.path.join(project_root, 'src/env/custom_integration')
retro.data.add_custom_integration(custom_path)

def discover_ram():
    print("Booting to discover correct RAM addresses...")
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=None, 
        inttype=retro.data.Integrations.CONTRIB_ONLY,
        render_mode='rgb_array'
    )
    env.reset()

    def press(buttons, duration=10, wait=60):
        for _ in range(duration):
            action = np.zeros(12, dtype=np.int8)
            for b in buttons:
                mapping = {"B":0, "Y":1, "A":8, "START":3, "UP":4, "DOWN":5}
                action[mapping[b]] = 1
            env.step(action)
        for _ in range(wait):
            env.step(np.zeros(12, dtype=np.int8))

    print("Advancing through intro and menus...")
    # This might take a while, but it's the only way to be sure
    for _ in range(1500): env.step(np.zeros(12, dtype=np.int8))
    
    press(["START"]) # Title
    press(["START"]) # Main Menu
    press(["A"]) # Mario GP
    press(["A"]) # 50cc
    press(["A"]) # Mario
    press(["A"]) # Mushroom Cup
    
    print("Waiting for race to start...")
    # Course overview and Lakitu countdown
    # This usually takes about 10 seconds (600 steps)
    
    addresses = {
        "X": 0x7E0088,
        "Y": 0x7E008C,
        "Lap": 0x7E10C1,
        "CP_User": 0x7E1020,
        "CP_Search": 0x7E10C0,
        "CP_Remote": 0x7E10DC,
        "Status": 0x7E10A6,
        "TCP_User": 0x7E1162,
        "TCP_Remote": 0x7E0148
    }

    print(f"{'Step':>5} | {'X':>6} | {'Y':>6} | {'Lap':>4} | {'CP_U':>4} | {'CP_S':>4} | {'CP_R':>4} | {'TCP_U':>5} | {'TCP_R':>5}")
    
    action = np.zeros(12, dtype=np.int8)
    action[0] = 1 # Hold Gas
    
    race_started = False
    for i in range(2000):
        obs, reward, terminated, truncated, info = env.step(action)
        
        ram = env.get_ram()
        def get_ram_val(addr, length=1):
            wram_addr = addr - 0x7E0000
            if length == 2:
                return ram[wram_addr] + (ram[wram_addr + 1] << 8)
            return ram[wram_addr]

        vals = {name: get_ram_val(addr, 2 if name in ["X", "Y"] else 1) for name, addr in addresses.items()}
        
        if i % 100 == 0 or (vals["X"] > 500 and not race_started):
            if vals["X"] > 500 and not race_started:
                print("--- RACE LIKELY STARTED ---")
                race_started = True
                cv2.imwrite("race_start_verified.png", cv2.cvtColor(obs, cv2.COLOR_RGB2BGR))
            
            print(f"{i:5} | {vals['X']:6} | {vals['Y']:6} | {vals['Lap']:4} | {vals['CP_User']:4} | {vals['CP_Search']:4} | {vals['CP_Remote']:4} | {vals['TCP_User']:5} | {vals['TCP_Remote']:5}")

    env.close()

if __name__ == "__main__":
    discover_ram()
