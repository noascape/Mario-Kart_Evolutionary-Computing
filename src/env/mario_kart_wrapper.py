import gymnasium as gym
import numpy as np

class MarioKartWrapper(gym.Wrapper):
    """
    Gymnasium wrapper for Super Mario Kart SNES.
    Extracts relevant RAM variables and manages custom fitness/reward.
    """
    def __init__(self, env, frame_skip=4):
        super(MarioKartWrapper, self).__init__(env)
        self.max_progress = 0
        self.steps_without_progress = 0
        self.max_stagnation_steps = 300 # 5 seconds
        self.frame_skip = frame_skip

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
        mod_action = action.copy()
        mod_action[0] = 1
        
        total_custom_reward = 0.0
        
        # Repeat the action for frame_skip steps
        for _ in range(self.frame_skip):
            obs, reward, terminated, truncated, info = self.env.step(mod_action)
            
            def get_val(name):
                try:
                    repo_name_map = {
                        "x": "kart1_X", "y": "kart1_Y", "angle": "kart1_direction",
                        "status": "surface", "checkpoint": "current_checkpoint",
                        "lap": "lap", "total_checkpoints": "totalCheckpoints",
                        "speed": "kart1_speed"
                    }
                    actual_name = repo_name_map.get(name, name)
                    var_info = self.env.unwrapped.data.get_variable(actual_name)
                    address = var_info['address']
                    var_type = var_info.get('type', '|u1')
                except ValueError:
                    fallbacks = {
                        "x": (136, "<u2"), "y": (140, "<u2"), "angle": (149, "|u1"),
                        "status": (4270, "|u1"), "checkpoint": (4316, "|u1"),
                        "lap": (4289, "|u1"), "total_checkpoints": (328, "|u1"),
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
            
            rel_lap = int(curr_lap) - 128
            tcp = int(total_checkpoints) if total_checkpoints > 0 else 26
            progress = (rel_lap * tcp) + int(curr_checkpoint)
            
            step_reward = 0.0
            
            if progress > self.max_progress:
                step_reward += 100.0 * float(progress - self.max_progress)
                self.max_progress = progress
                self.steps_without_progress = 0
            else:
                self.steps_without_progress += 1

            if curr_status != 64 and curr_lap >= 128: 
                step_reward -= 1.0 
                # No longer terminating immediately to allow for recovery and corner-cutting experiments
                
            if not terminated and curr_speed > 100:
                step_reward += (curr_speed / 1000.0)

            if self.steps_without_progress > self.max_stagnation_steps:
                terminated = True
            
            total_custom_reward += step_reward
            
            if terminated or truncated:
                break
        
        total_custom_reward = float(round(total_custom_reward))
        
        info.update({
            'x': get_val("x"), 'y': get_val("y"), 'angle': get_val("angle"),
            'status': curr_status, 'checkpoint': curr_checkpoint,
            'lap': curr_lap, 'speed': curr_speed, 'progress': progress
        })
        
        return obs, total_custom_reward, terminated, truncated, info
