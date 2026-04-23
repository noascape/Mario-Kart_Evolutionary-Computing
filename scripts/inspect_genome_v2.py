import pickle
import neat
import os
import sys
import numpy as np

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.evolution.representations.neat_approach.genome import NEATGenome

def inspect():
    config_path = os.path.join(project_root, 'config/neat-feedforward.cfg')
    genome_path = os.path.join(project_root, 'best_genome.pkl')
    
    if not os.path.exists(genome_path):
        print("No best_genome.pkl found!")
        return

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    with open(genome_path, 'rb') as f:
        genome = pickle.load(f)
    
    nn = NEATGenome(genome, config)
    
    print(f"--- Genome {genome.key} Inspection ---")
    print(f"Nodes: {len(genome.nodes)}")
    print(f"Connections: {len(genome.connections)}")
    
    # Simulate a starting state
    # X, Y, Angle, Status, Checkpoint, Lap, Speed
    test_ram = {
        'x': 1000, 
        'y': 1000, 
        'angle': 0, 
        'status': 0, 
        'checkpoint': 0, 
        'lap': 128, 
        'speed': 0
    }
    
    action = nn.get_action({'ram_state': test_ram})
    buttons = ["B", "Y", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT", "A", "X", "L", "R"]
    pressed = [buttons[i] for i, val in enumerate(action) if val > 0]
    
    print(f"Inputs: {test_ram}")
    print(f"Outputs (Buttons Pressed): {pressed}")
    
    if not pressed:
        print("CRITICAL: NO BUTTONS PRESSED! The agent is paralyzed.")
    elif "B" not in pressed:
        print("WARNING: 'B' (Gas) not pressed. The agent won't move.")

if __name__ == "__main__":
    inspect()
