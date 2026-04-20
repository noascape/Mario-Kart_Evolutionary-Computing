import gymnasium as gym
import numpy as np

class MarioKartWrapper(gym.Wrapper):
    """
    Gymnasium wrapper for Super Mario Kart SNES.
    Extracts relevant RAM variables and manages custom fitness/reward.
    """
    def __init__(self, env):
        super(MarioKartWrapper, self).__init__(env)
        self.prev_checkpoint = 0
        self.prev_lap = 0
        self.prev_x = 0
        self.prev_y = 0
        self.max_progress = 0
        self.steps_without_progress = 0
        self.max_stagnation_steps = 1000 # Increased to 16 seconds

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        
        def get_val(name):
            try:
                var_info = self.env.unwrapped.data.get_variable(name)
                address = var_info['address']
                var_type = var_info.get('type', '|u1')
            except ValueError:
                # Fallback to hardcoded addresses if data.json mapping fails
                fallbacks = {
                    "x": (0x7E0088, "<u2"),
                    "y": (0x7E008C, "<u2"),
                    "angle": (0x7E112A, "<u2"),
                    "status": (0x7E10A6, "|u1"),
                    "checkpoint": (0x7E1020, "|u1"),
                    "lap": (0x7E10C1, "|u1"),
                    "total_checkpoints": (0x7E1162, "|u1")
                }
                if name in fallbacks:
                    address, var_type = fallbacks[name]
                else:
                    return 0
            
            ram = self.env.unwrapped.get_ram()
            wram_addr = address - 0x7E0000
            if var_type == '<u2':
                return ram[wram_addr] + (ram[wram_addr + 1] << 8)
            else:
                return ram[wram_addr]

        self.prev_x = get_val("x")
        self.prev_y = get_val("y")
        self.prev_checkpoint = get_val("checkpoint")
        self.prev_lap = get_val("lap")
        self.max_progress = 0
        self.steps_without_progress = 0
        
        info['x'] = self.prev_x
        info['y'] = self.prev_y
        info['angle'] = get_val("angle")
        info['status'] = get_val("status")
        info['checkpoint'] = self.prev_checkpoint
        info['lap'] = self.prev_lap
        info['total_checkpoints'] = get_val("total_checkpoints")
        
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        
        def get_val(name):
            try:
                var_info = self.env.unwrapped.data.get_variable(name)
                address = var_info['address']
                var_type = var_info.get('type', '|u1')
            except ValueError:
                fallbacks = {
                    "x": (0x7E0088, "<u2"),
                    "y": (0x7E008C, "<u2"),
                    "angle": (0x7E112A, "<u2"),
                    "status": (0x7E10A6, "|u1"),
                    "checkpoint": (0x7E1020, "|u1"),
                    "lap": (0x7E10C1, "|u1"),
                    "total_checkpoints": (0x7E1162, "|u1"),
                    "speed": (0x7E10EA, "<u2")
                }
                if name in fallbacks:
                    address, var_type = fallbacks[name]
                else:
                    return 0
            
            ram = self.env.unwrapped.get_ram()
            wram_addr = address - 0x7E0000
            if var_type == '<u2':
                return ram[wram_addr] + (ram[wram_addr + 1] << 8)
            else:
                return ram[wram_addr]

        curr_x = get_val("x")
        curr_y = get_val("y")
        curr_checkpoint = get_val("checkpoint")
        curr_lap = get_val("lap")
        total_checkpoints = get_val("total_checkpoints")
        curr_speed = get_val("speed")
        curr_status = get_val("status")
        
        # 1. Progress Calculation
        rel_lap = curr_lap - 127 if curr_lap >= 127 else 0
        progress = (rel_lap * (total_checkpoints if total_checkpoints > 0 else 26)) + curr_checkpoint
        
        # 2. Fitness Components
        custom_reward = 0.0
        
        # Checkpoint Reward (The main goal)
        if progress > self.max_progress:
            # Huge boost for reaching a new checkpoint
            custom_reward += 50.0 * float(progress - self.max_progress)
            self.max_progress = progress
            self.steps_without_progress = 0
        else:
            self.steps_without_progress += 1
            # Time penalty (Encourages speed)
            custom_reward -= 0.1

        # Speed Reward (Encourages moving, but scaled down)
        # Only give speed reward if we are not "stuck"
        if curr_speed > 0:
            custom_reward += (curr_speed / 1000.0)

        # Crash/Wall Penalty
        # If speed is near zero but gas (action[0]) is held, or status is high
        if action[0] > 0 and curr_speed < 10 and self.steps_without_progress > 30:
            custom_reward -= 0.5
            
        if curr_status >= 0x40: # Typical 'hit wall' or 'spinning' status
            custom_reward -= 1.0

        # 3. Termination Logic
        # Kill if no progress for 4 seconds
        if self.steps_without_progress > 240:
            terminated = True
        
        # Update info
        info['x'] = curr_x
        info['y'] = curr_y
        info['angle'] = get_val("angle")
        info['status'] = curr_status
        info['checkpoint'] = curr_checkpoint
        info['lap'] = curr_lap
        info['speed'] = curr_speed
        info['progress'] = progress
        
        return obs, custom_reward, terminated, truncated, info
