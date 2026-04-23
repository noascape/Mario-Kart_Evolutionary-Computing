import argparse
import importlib
import neat
import os
import sys
import multiprocessing
import numpy as np
import cv2
import time
import pickle

# Ensure the root of the project is in the Python path for imports to work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Ensure retro is available
try:
    import stable_retro as retro
except ImportError:
    import retro

from src.env.mario_kart_wrapper import MarioKartWrapper

# Register custom integration
custom_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration'))
retro.data.add_custom_integration(custom_path)

def make_env():
    """Helper to create and wrap the environment."""
    try:
        # Use SuperMarioKart-Snes-v0 as registered
        state_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration/SuperMarioKart-Snes-v0/start_race.state'))
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=state_path, 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode='rgb_array'
        )
        env = MarioKartWrapper(inner_env)
        return env
    except Exception as e:
        # Silently fail for parallel processes, but ideally log this
        return None

def eval_genome_neat(genome, config):
    """
    Specialized evaluator for NEAT.
    Must be globally accessible for multiprocessing to pickle it.
    """
    from src.evolution.representations.neat_approach.genome import NEATGenome
    
    env = make_env()
    if env is None:
        return 0.0
    
    wrapped_genome = NEATGenome(genome, config)
    
    obs, info = env.reset()
    total_fitness = 0.0
    
    # Run for a fixed number of steps (e.g., 10000 steps for multiple laps)
    # The wrapper will terminate the episode if it stops making progress (300 steps stagnation)
    max_steps = 10000 
    for i in range(max_steps):
        # Observation is expected to be {'obs': image_data, 'ram_state': info}
        action = wrapped_genome.get_action({'obs': obs, 'ram_state': info})
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        # In our refactored wrapper, 'reward' IS the custom fitness
        total_fitness += reward
        
        if terminated or truncated:
            break
            
    env.close()
    
    return float(total_fitness)

class EvolutionReporter(neat.reporting.BaseReporter):
    """
    NEAT Reporter that captures a 'replay' of the best genome, 
    saves the genome itself, and logs generation stats to a file.
    """
    def __init__(self, replay_frequency=5, save_frequency=1):
        self.replay_frequency = replay_frequency
        self.save_frequency = save_frequency
        self.generation = 0
        self.global_best_fitness = -float('inf')
        self.stagnation_count = 0

    def post_evaluate(self, config, population, species, best_genome):
        # Create subfolder for this generation
        gen_dir = os.path.join(project_root, f'Gameplay/evolution/gen_{self.generation}')
        os.makedirs(gen_dir, exist_ok=True)

        # 1. Calculate advanced stats
        if best_genome.fitness is not None:
            if best_genome.fitness > self.global_best_fitness:
                self.global_best_fitness = best_genome.fitness
                self.stagnation_count = 0
            else:
                self.stagnation_count += 1

        avg_fitness = np.mean([g.fitness for g in population.values() if g.fitness is not None])
        avg_nodes = np.mean([len(g.nodes) for g in population.values()])
        avg_conns = np.mean([len(g.connections) for g in population.values()])
        num_species = len(species.species)
        
        # Approximate checkpoints (Fitness = 100 * Progress + SpeedBonus)
        approx_checkpoints = int(best_genome.fitness // 100) if best_genome.fitness else 0

        # 2. Save stats to json in the folder
        import json
        stats = {
            "generation": self.generation,
            "best_fitness": best_genome.fitness,
            "avg_fitness": float(avg_fitness),
            "num_species": num_species,
            "stagnation": self.stagnation_count,
            "best_complexity": best_genome.size(), # (nodes, connections)
            "avg_nodes": float(avg_nodes),
            "avg_conns": float(avg_conns),
            "approx_max_checkpoints": approx_checkpoints,
            "best_genome_id": best_genome.key
        }
        with open(os.path.join(gen_dir, 'stats.json'), 'w') as f:
            json.dump(stats, f, indent=4)

        # 3. Always save best genome of the generation
        if self.generation % self.save_frequency == 0:
            self._save_best_genome(best_genome, gen_dir)
            
        # 4. Periodically capture replay frames
        if self.generation % self.replay_frequency == 0:
            print(f"\n--- Capturing Generation {self.generation} Replay ---")
            self._capture_replay(best_genome, config, gen_dir)
        
        self.generation += 1

    def _save_best_genome(self, genome, gen_dir):
        genome_path = os.path.join(gen_dir, 'best_genome.pkl')
        with open(genome_path, 'wb') as f:
            pickle.dump(genome, f)
        # Also symlink or copy to a 'latest_best' for easy access
        latest_path = os.path.join(project_root, 'best_genome.pkl')
        with open(latest_path, 'wb') as f:
            pickle.dump(genome, f)

    def _capture_replay(self, genome, config, gen_dir):
        from src.evolution.representations.neat_approach.genome import NEATGenome
        
        env = make_env()
        if env is None: return
        
        wrapped_genome = NEATGenome(genome, config)
        obs, info = env.reset()
        
        for i in range(2000): # Max capture steps
            action = wrapped_genome.get_action({'obs': obs, 'ram_state': info})
            obs, reward, terminated, truncated, info = env.step(action)
            
            if i % 50 == 0:
                frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
                fname = os.path.join(gen_dir, f"frame_{i}.png")
                cv2.imwrite(fname, frame_bgr)
            
            if terminated or truncated:
                # Save the final frame where it died/terminated
                frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
                fname = os.path.join(gen_dir, f"frame_final_{i}.png")
                cv2.imwrite(fname, frame_bgr)
                print(f"Replay terminated at step {i}")
                break
        env.close()
        print(f"--- Replay Saved to {gen_dir} ---")

class TimeReporter(neat.reporting.BaseReporter):
    """
    Stops training after a certain amount of time.
    """
    def __init__(self, max_seconds):
        self.max_seconds = max_seconds
        self.start_time = time.time()

    def end_generation(self, config, population, species):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_seconds:
            print(f"\n--- Time Limit Reached ({elapsed/60:.2f} minutes). Stopping Training. ---")
            # We can't easily stop neat-python from a reporter other than raising an exception
            # or setting a flag that the population loop checks.
            # Raising an exception is a bit hacky but works.
            raise KeyboardInterrupt("Time limit reached")

class SummaryReporter(neat.reporting.BaseReporter):
    """
    Logs a concise summary of the evolution to a CSV file every N generations.
    """
    def __init__(self, filename='training_summary.csv', frequency=10):
        self.filename = os.path.join(project_root, filename)
        self.frequency = frequency
        self.generation = 0
        # Initialize the file with a header if it doesn't exist
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                f.write("generation,best_fitness,avg_fitness,num_species,best_nodes,best_conns,max_cp\n")

    def post_evaluate(self, config, population, species, best_genome):
        if self.generation % self.frequency == 0:
            avg_fitness = np.mean([g.fitness for g in population.values() if g.fitness is not None])
            num_species = len(species.species)
            nodes, conns = best_genome.size()
            max_cp = int(best_genome.fitness // 100) if best_genome.fitness else 0
            
            with open(self.filename, 'a') as f:
                f.write(f"{self.generation},{best_genome.fitness},{avg_fitness},{num_species},{nodes},{conns},{max_cp}\n")
            print(f"--- Summary logged to {self.filename} ---")
        self.generation += 1

class Trainer:
    def __init__(self, args):
        self.args = args
        self.config_path = os.path.abspath(args.config)
        
    def train_neat(self):
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             self.config_path)
        
        pop = neat.Population(config)
        pop.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        pop.add_reporter(stats)
        
        # Add our improved EvolutionReporter
        # frequency=5 means replay every 5 generations
        pop.add_reporter(EvolutionReporter(replay_frequency=5, save_frequency=1))
        
        # Add SummaryReporter
        # frequency=5 means log to CSV every 5 generations
        pop.add_reporter(SummaryReporter(frequency=5))
        
        # Add TimeReporter if duration is specified
        if self.args.duration > 0:
            pop.add_reporter(TimeReporter(self.args.duration * 60))
        
        # Checkpointing
        checkpoint_dir = os.path.abspath('checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        pop.add_reporter(neat.Checkpointer(5, filename_prefix=f'{checkpoint_dir}/neat-checkpoint-'))
        
        # Parallel evaluation
        pe = neat.ParallelEvaluator(self.args.parallel, eval_genome_neat)
        
        print(f"--- Starting Super Mario Kart Evolution ---")
        print(f"Representation: {self.args.rep}")
        print(f"Parallelism:    {self.args.parallel} cores")
        print(f"Generations:    {self.args.generations}")
        if self.args.duration > 0:
            print(f"Time Limit:     {self.args.duration} minutes")
        print(f"--- ---------------------------------- ---")
        
        try:
            winner = pop.run(pe.evaluate, self.args.generations)
        except KeyboardInterrupt as e:
            print(f"Training interrupted: {e}")
            winner = pop.best_genome
        
        # Save winner
        output_file = 'best_genome.pkl'
        with open(output_file, 'wb') as f:
            pickle.dump(winner, f)
        
        print(f'\nBest genome saved as {output_file}')

    def run(self):
        if self.args.rep == 'neat_approach':
            self.train_neat()
        else:
            print(f"Representation '{self.args.rep}' not supported by current CLI.")

def main():
    parser = argparse.ArgumentParser(description='Super Mario Kart Evolutionary Trainer')
    parser.add_argument('--rep', type=str, default='neat_approach', help='Evolutionary representation (neat_approach)')
    parser.add_argument('--config', type=str, default='config/neat-feedforward.cfg', help='Path to NEAT config')
    parser.add_argument('--parallel', type=int, default=multiprocessing.cpu_count(), help='Parallel worker count')
    parser.add_argument('--generations', type=int, default=1000, help='Max generations to run')
    parser.add_argument('--duration', type=int, default=0, help='Max duration in minutes (0 for no limit)')
    
    args = parser.parse_args()
    trainer = Trainer(args)
    trainer.run()

if __name__ == '__main__':
    main()
