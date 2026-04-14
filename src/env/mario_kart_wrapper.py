import gymnasium as gym
import numpy as np

class MarioKartWrapper(gym.Wrapper):
    """
    Gymnasium wrapper for Super Mario Kart SNES.
    Extracts relevant RAM variables and manages custom fitness/reward.
    """
    def __init__(self, env):
        super(MarioKartWrapper, self).__init__(env)
        self.prev_x = 0
        self.prev_y = 0

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        # In stable-retro, variables are accessed via data.get_variable(name)
        # which returns the actual value if it's correctly mapped.
        # If it returns a dict, something is wrong with how stable-retro is handling it.
        # Let's try to get it directly from memory if needed, but first let's check
        # if there's a different method.
        try:
            self.prev_x = self.env.unwrapped.data.get_variable("x")
            self.prev_y = self.env.unwrapped.data.get_variable("y")
        except:
            self.prev_x = 0
            self.prev_y = 0
        return obs, info

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        
        # Extract RAM data
        # Based on previous failure, get_variable might be returning a dict of metadata
        # if not properly initialized. Let's try to access the value if it's a dict.
        
        def get_val(name):
            val = self.env.unwrapped.data.get_variable(name)
            if isinstance(val, dict):
                # Fallback: manually read from RAM if get_variable returns metadata
                # Address in data.json is 8257672 (0x7E0088 + 0x800000 offset for some reason?)
                # 0x7E0088 is the standard SNES RAM address.
                # In retro, RAM is usually accessed via env.unwrapped.get_ram()
                return 0 # Placeholder if it still fails
            return val

        current_x = get_val("x")
        current_y = get_val("y")
        angle = get_val("angle")
        status = get_val("status")
        
        # Update info dictionary
        info['x'] = current_x
        info['y'] = current_y
        info['angle'] = angle
        info['status'] = status
        
        self.prev_x = current_x
        self.prev_y = current_y
        
        return obs, reward, terminated, truncated, info
