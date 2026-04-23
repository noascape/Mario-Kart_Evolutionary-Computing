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
        Maps RAM-based observation to NEAT outputs with mutual exclusion for directions.
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
        inputs[6] /= 2000.0

        outputs = self.net.activate(inputs)
        
        # Map outputs to binary button states
        # Index Mapping for Retro:
        # 0:B, 1:Y, 2:SELECT, 3:START, 4:UP, 5:DOWN, 6:LEFT, 7:RIGHT, 8:A, 9:X, 10:L, 11:R
        actions = np.zeros(12, dtype=np.int8)
        
        threshold = 0.5
        
        # Helper for basic buttons (DISABLED 2:SELECT and 3:START)
        for i in [0, 1, 8, 9, 10, 11]:
            if outputs[i] > threshold:
                actions[i] = 1
        
        # Mutual Exclusion for D-Pad
        # UP (4) vs DOWN (5)
        if outputs[4] > outputs[5] and outputs[4] > threshold:
            actions[4] = 1
        elif outputs[5] > outputs[4] and outputs[5] > threshold:
            actions[5] = 1
            
        # LEFT (6) vs RIGHT (7)
        if outputs[6] > outputs[7] and outputs[6] > threshold:
            actions[6] = 1
        elif outputs[7] > outputs[6] and outputs[7] > threshold:
            actions[7] = 1
            
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
