import pytest
import numpy as np
import gymnasium as gym
from typing import Dict, Any
from src.env.mario_kart_wrapper import MarioKartWrapper

try:
    import stable_retro as retro
except ImportError:
    import retro

def test_wrapper_ram_extraction():
    """Test that the wrapper correctly extracts RAM variables."""
    try:
        inner_env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE)
        env = MarioKartWrapper(inner_env)
        
        env.reset()
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert 'x' in info, "Info should contain 'x' position"
        assert 'y' in info, "Info should contain 'y' position"
        assert 'angle' in info, "Info should contain 'angle'"
        assert 'status' in info, "Info should contain 'status'"
        
        # Verify types (based on data.json mapping)
        assert isinstance(info['x'], (int, np.integer))
        assert isinstance(info['y'], (int, np.integer))
        
        env.close()
    except Exception as e:
        pytest.fail(f"Wrapper test failed: {e}")

if __name__ == "__main__":
    test_wrapper_ram_extraction()
