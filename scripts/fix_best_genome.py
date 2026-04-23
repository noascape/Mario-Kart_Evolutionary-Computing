import neat
import pickle
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dummy class to satisfy pickle if the checkpoint was saved with a custom reporter
class CaptureReporter(neat.reporting.BaseReporter):
    pass

def extract_best():
    checkpoint_dir = 'checkpoints'
    checkpoints = [f for f in os.listdir(checkpoint_dir) if f.startswith('neat-checkpoint-')]
    if not checkpoints:
        print("No checkpoints found.")
        return
    
    checkpoints.sort(key=lambda x: int(x.split('-')[-1]))
    latest = os.path.join(checkpoint_dir, checkpoints[-1])
    print(f"Restoring from {latest}")
    
    # We need to ensure the class is available in __main__ for pickle
    import __main__
    setattr(__main__, 'CaptureReporter', CaptureReporter)
    
    p = neat.Checkpointer.restore_checkpoint(latest)
    best_genome = None
    max_fitness = -float('inf')
    
    for g in p.population.values():
        if g.fitness is not None and g.fitness > max_fitness:
            max_fitness = g.fitness
            best_genome = g
            
    if best_genome:
        print(f"Saving best genome {best_genome.key} with fitness {best_genome.fitness}")
        with open('best_genome.pkl', 'wb') as f:
            pickle.dump(best_genome, f)
    else:
        print("No genomes with fitness found in checkpoint.")

if __name__ == "__main__":
    extract_best()
