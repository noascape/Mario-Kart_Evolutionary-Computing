import gymnasium as gym
import numpy as np

class MarioKartWrapper(gym.Wrapper):
    """
    Gymnasium wrapper for Super Mario Kart SNES.
    Extracts relevant RAM variables and manages custom fitness/reward.
    """
    def __init__(self, env):
        super(MarioKartWrapper, self).__init__(env)
        self.max_progress = 0
        self.steps_without_progress = 0
        self.max_stagnation_steps = 300 # 5 seconds

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        
        def get_val(name):
            fallbacks = {
                "x": (136, "<u2"),
                "y": (140, "<u2"),
                "checkpoint": (4316, "|u1"),
                "lap": (4289, "|u1"),
                "status": (4270, "|u1"),
                "total_checkpoints": (328, "|u1")
            }
            addr, vtype = fallbacks[name]
            ram = self.env.unwrapped.get_ram()
            if vtype == '<u2':
                return ram[addr] + (ram[addr + 1] << 8)
            else:
                return ram[addr]

        self.steps_without_progress = 0
        
        curr_checkpoint = get_val("checkpoint")
        curr_lap = get_val("lap")
        total_checkpoints = get_val("total_checkpoints")
        
        # Continuous lap logic: Lap 128 is Lap 1 (rel_lap 0), Lap 127 is Pre-race (rel_lap -1)
        rel_lap = int(curr_lap) - 128
        tcp = int(total_checkpoints) if total_checkpoints > 0 else 26
        self.max_progress = (rel_lap * tcp) + int(curr_checkpoint)
        
        info['checkpoint'] = curr_checkpoint
        info['lap'] = curr_lap
        info['progress'] = self.max_progress
        
        return obs, info

    def step(self, action):
        # Force Gas (B) button to be always 1 (Gas Bias)
        # B is at index 0 in SMK retro mapping
        mod_action = action.copy()
        mod_action[0] = 1
        
        obs, reward, terminated, truncated, info = self.env.step(mod_action)
        
        def get_val(name):
            try:
                # Map our internal names to repository names in data.json
                repo_name_map = {
                    "x": "kart1_X",
                    "y": "kart1_Y",
                    "angle": "kart1_direction",
                    "status": "surface",
                    "checkpoint": "current_checkpoint",
                    "lap": "lap",
                    "total_checkpoints": "totalCheckpoints",
                    "speed": "kart1_speed"
                }
                actual_name = repo_name_map.get(name, name)
                var_info = self.env.unwrapped.data.get_variable(actual_name)
                address = var_info['address']
                var_type = var_info.get('type', '|u1')
            except ValueError:
                fallbacks = {
                    "x": (136, "<u2"),
                    "y": (140, "<u2"),
                    "angle": (149, "|u1"),
                    "status": (4270, "|u1"),
                    "checkpoint": (4316, "|u1"),
                    "lap": (4289, "|u1"),
                    "total_checkpoints": (328, "|u1"),
                    "speed": (4330, "<u2")
                }
                if name in fallbacks:
                    address, var_type = fallbacks[name]
                else:
                    return 0
            
            ram = self.env.unwrapped.get_ram()
            if var_type == '<u2' or var_type == '<i2':
                return ram[address] + (ram[address + 1] << 8)
            else:
                return ram[address]

        curr_checkpoint = get_val("checkpoint")
        curr_lap = get_val("lap")
        total_checkpoints = get_val("total_checkpoints")
        curr_speed = get_val("speed")
        curr_status = get_val("status")
        
        # 1. Progress Calculation
        rel_lap = int(curr_lap) - 128
        tcp = int(total_checkpoints) if total_checkpoints > 0 else 26
        progress = (rel_lap * tcp) + int(curr_checkpoint)
        
        custom_reward = 0.0
        
        # 2. Major Reward: Checkpoint Progress
        if progress > self.max_progress:
            # Reaching a new checkpoint is the ONLY major way to get a huge reward
            custom_reward += 100.0 * float(progress - self.max_progress)
            self.max_progress = progress
            self.steps_without_progress = 0
        else:
            self.steps_without_progress += 1

        # 3. Surface Logic (SMK Address 0x10AE)
        # 0x40 (64) = Road. Grass is usually 0x80+ or 0x50+
        if curr_status != 64 and curr_lap >= 128: 
            # ANY off-road surface terminates immediately to encourage staying on track
            custom_reward -= 50.0 
            terminated = True
            
        # Speed Reward: Only if NOT crashing and ONLY as a small gradient
        if not terminated and curr_speed > 100:
            custom_reward += (curr_speed / 1000.0)

        # 4. Termination Logic
        if self.steps_without_progress > self.max_stagnation_steps:
            terminated = True
        
        # Quantize reward to prevent tiny noise from resetting NEAT stagnation
        custom_reward = float(round(custom_reward))
        
        # Update info for the agent
        info['x'] = get_val("x")
        info['y'] = get_val("y")
        info['angle'] = get_val("angle")
        info['status'] = curr_status
        info['checkpoint'] = curr_checkpoint
        info['lap'] = curr_lap
        info['speed'] = curr_speed
        info['progress'] = progress
        
        return obs, custom_reward, terminated, truncated, info
