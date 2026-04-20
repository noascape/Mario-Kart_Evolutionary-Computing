import neat
import numpy as np
import pickle
from src.evolution.base import BaseGenome

class NEATGenome(BaseGenome):
    """
    Wrapper for a NEAT-evolved Neural Network.
    """
    def __init__(self, genome, config):
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(genome, config)

    def get_action(self, observation):
        """
        Maps RAM-based observation to NEAT outputs.
        Expects observation to contain 'ram_state'.
        """
        ram = observation.get('ram_state', {})
        # Use 7 RAM inputs: X, Y, Angle, Status, Checkpoint, Lap, Speed
        inputs = [
            float(ram.get('x', 0)),
            float(ram.get('y', 0)),
            float(ram.get('angle', 0)),
            float(ram.get('status', 0)),
            float(ram.get('checkpoint', 0)),
            float(ram.get('lap', 0)),
            float(ram.get('speed', 0))
        ]
        
        # Normalize inputs
        inputs[0] /= 10000.0 
        inputs[1] /= 10000.0
        inputs[2] /= 65535.0
        inputs[3] /= 255.0
        inputs[4] /= 30.0
        inputs[5] /= 200.0
        inputs[6] /= 2000.0 # SMK speed is typically 0-1500 approx

        outputs = self.net.activate(inputs)
        
        # Map outputs to binary button states
        # B, Y, SELECT, START, UP, DOWN, LEFT, RIGHT, A, X, L, R
        actions = np.zeros(12, dtype=np.int8)
        
        # Gasoline (B button)
        if outputs[0] > 0.4:
            actions[0] = 1
            
        # Other buttons
        for i in range(1, 12):
            if outputs[i] > 0.5:
                actions[i] = 1
        return actions

    def mutate(self):
        """Mutation is handled by the NEAT Population object, not individually."""
        pass

    def crossover(self, other):
        """Crossover is handled by the NEAT Population object."""
        pass

    def save(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self.genome, f)

    @classmethod
    def load(cls, file_path, config):
        with open(file_path, 'rb') as f:
            genome = pickle.load(f)
        return cls(genome, config)
