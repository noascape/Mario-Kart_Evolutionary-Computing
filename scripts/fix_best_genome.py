import neat
import pickle
import os

def extract_best():
    checkpoint = 'checkpoints/neat-checkpoint-5'
    if not os.path.exists(checkpoint):
        print(f"Checkpoint {checkpoint} not found.")
        return
        
    p = neat.Checkpointer.restore_checkpoint(checkpoint)
    best = None
    for g in p.population.values():
        if g.fitness is not None:
            if best is None or g.fitness > best.fitness:
                best = g
                
    if best:
        print(f"Saving best genome {best.key} with fitness {best.fitness}")
        with open('best_genome.pkl', 'wb') as f:
            pickle.dump(best, f)
    else:
        print("No genome with fitness found.")

if __name__ == "__main__":
    extract_best()
