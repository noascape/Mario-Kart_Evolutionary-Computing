import numpy as np
from src.evolution.base import BaseGenome

class TemplateGenome(BaseGenome):
    """
    Standard template for implementing a new genomic representation.
    """
    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            # Initialize with random values (e.g., 2D matrix or weights)
            self.data = np.random.rand(10) 

    def get_action(self, observation):
        """
        Input: Multi-modal observation from EvolutionBridge.
        Output: 12 button states [B, Y, SELECT, START, UP, DOWN, LEFT, RIGHT, A, X, L, R]
        """
        # Example logic: press 'B' (index 0) if first value > 0.5
        actions = np.zeros(12, dtype=np.int8)
        if self.data[0] > 0.5:
            actions[0] = 1
        return actions

    def mutate(self):
        """Applies Gaussian noise or other variation."""
        self.data += np.random.normal(0, 0.1, size=self.data.shape)

    def crossover(self, other):
        """Simple uniform crossover."""
        child_data = np.where(np.random.rand(10) > 0.5, self.data, other.data)
        return TemplateGenome(child_data)

    def save(self, file_path):
        np.save(file_path, self.data)

    @classmethod
    def load(cls, file_path):
        data = np.load(file_path)
        return cls(data)
