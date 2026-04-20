import pytest
import numpy as np
import os

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    import stable_retro as retro
except ImportError:
    import retro

def test_retro_load():
    """Test that SuperMarioKart-Snes-v0 can be loaded and reset."""
    # Register custom integration
    custom_path = os.path.abspath('src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    try:
        env = retro.make(game='SuperMarioKart-Snes-v0', state=retro.State.NONE, inttype=retro.data.Integrations.CONTRIB_ONLY)
        obs, info = env.reset()
        
        assert isinstance(obs, np.ndarray), "Observation should be a numpy array"
        # SNES resolution is typically 256x224
        assert obs.shape == (224, 256, 3), f"Expected shape (224, 256, 3), got {obs.shape}"
        
        env.close()
    except Exception as e:
        pytest.fail(f"Failed to load environment: {e}")

if __name__ == "__main__":
    test_retro_load()
