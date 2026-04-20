import pickle
import neat
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def inspect():
    with open('best_genome.pkl', 'rb') as f:
        genome = pickle.load(f)
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         'config/neat-feedforward.cfg')
    
    print(f"Genome ID: {genome.key}")
    print(f"Fitness:   {genome.fitness}")
    print("\nNodes:")
    for node_id, node in genome.nodes.items():
        print(f"  Node {node_id}: Bias={node.bias}, Response={node.response}, Activation={node.activation}")
    
    print("\nConnections:")
    for conn_id, conn in genome.connections.items():
        if conn.enabled:
            print(f"  {conn_id}: Weight={conn.weight}")

if __name__ == "__main__":
    inspect()
