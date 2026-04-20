import pytest
import numpy as np
import os
import stable_retro as retro
from src.env.base_wrapper import EvolutionBridge

def test_evolution_bridge_methods():
    """Test that EvolutionBridge provides the required observation methods."""
    # Register custom integration
    custom_path = os.path.abspath('src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    # Try to load the environment
    # Note: Using inttype=retro.data.Integrations.ALL if available, otherwise just use 'contrib'
    try:
        env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE, inttype=retro.data.Integrations.CONTRIB_ONLY)
    except Exception as e:
        pytest.skip(f"Could not load environment (ROM probably missing): {e}")
        return

    bridge = EvolutionBridge(env)
    
    obs, info = bridge.reset()
    
    # 1. Visual State (downsampled/grayscale)
    visual_state = bridge.get_visual_state(obs)
    assert isinstance(visual_state, np.ndarray), "Visual state should be a numpy array"
    assert visual_state.shape == (64, 64), f"Expected shape (64, 64), got {visual_state.shape}"
    
    # 2. RAM State
    ram_state = bridge.get_ram_state()
    assert isinstance(ram_state, dict), "RAM state should be a dictionary"
    assert 'x' in ram_state, "RAM state missing 'x'"
    assert 'y' in ram_state, "RAM state missing 'y'"
    
    # 3. Raycast State
    raycast_state = bridge.get_raycast_state()
    assert isinstance(raycast_state, np.ndarray), "Raycast state should be a numpy array"
    
    env.close()

if __name__ == "__main__":
    pytest.main([__file__])
