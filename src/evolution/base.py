from abc import ABC, abstractmethod
import numpy as np

class BaseGenome(ABC):
    """
    Abstract Base Class for all Genome representations.
    """
    @abstractmethod
    def get_action(self, observation):
        """
        Maps an observation (Visual, RAM, or Raycast) to SNES actions.
        Returns: np.ndarray of 12 button states.
        """
        pass

    @abstractmethod
    def mutate(self):
        """Applies representation-specific mutation."""
        pass

    @abstractmethod
    def crossover(self, other):
        """Combines this genome with another."""
        pass

    @abstractmethod
    def save(self, file_path):
        """Serializes the genome."""
        pass

    @classmethod
    @abstractmethod
    def load(cls, file_path):
        """Deserializes the genome."""
        pass

class BaseEvolution(ABC):
    """
    Abstract Base Class for evolutionary algorithms.
    """
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def evaluate_generation(self, genomes, fitness_fn):
        """Runs one generation of evolution."""
        pass

    @abstractmethod
    def select_best(self, genomes):
        """Selection logic for the next generation."""
        pass
