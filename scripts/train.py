import argparse
import importlib
import neat
import os
import sys
import multiprocessing
import numpy as np
import cv2

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
        
        # In our refactored wrapper, 'reward' IS the number of new checkpoints passed
        total_fitness += reward
        
        if terminated or truncated:
            break
            
    env.close()
    
    return float(total_fitness)

class CaptureReporter(neat.reporting.BaseReporter):
    """
    NEAT Reporter that captures a 'replay' of the best genome every N generations.
    """
    def __init__(self, frequency=5):
        self.frequency = frequency
        self.generation = 0

    def post_evaluate(self, config, population, species, best_genome):
        if self.generation % self.frequency == 0:
            print(f"\n--- Capturing Generation {self.generation} Replay ---")
            self._capture_replay(best_genome, config)
        self.generation += 1

    def _capture_replay(self, genome, config):
        from src.evolution.representations.neat_approach.genome import NEATGenome
        
        # Create subfolder for this generation
        gen_dir = os.path.join(project_root, f'Gameplay/evolution/gen_{self.generation}')
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)

        env = make_env()
        if env is None: return
        
        wrapped_genome = NEATGenome(genome, config)
        obs, info = env.reset()
        
        for i in range(1000): # Capture up to 1000 steps
            action = wrapped_genome.get_action({'obs': obs, 'ram_state': info})
            obs, reward, terminated, truncated, info = env.step(action)
            
            if i % 50 == 0:
                frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
                fname = os.path.join(gen_dir, f"frame_{i}.png")
                cv2.imwrite(fname, frame_bgr)
            
            if terminated or truncated:
                break
        env.close()
        print(f"--- Replay Saved to {gen_dir} ---")

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
        
        # Add our custom CaptureReporter
        pop.add_reporter(CaptureReporter(frequency=5))
        
        # Checkpointing
        checkpoint_dir = os.path.abspath('checkpoints')
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
        pop.add_reporter(neat.Checkpointer(5, filename_prefix=f'{checkpoint_dir}/neat-checkpoint-'))
        
        # Parallel evaluation
        pe = neat.ParallelEvaluator(self.args.parallel, eval_genome_neat)
        
        print(f"--- Starting Super Mario Kart Evolution ---")
        print(f"Representation: {self.args.rep}")
        print(f"Parallelism:    {self.args.parallel} cores")
        print(f"Generations:    {self.args.generations}")
        print(f"--- ---------------------------------- ---")
        
        winner = pop.run(pe.evaluate, self.args.generations)
        
        # Save winner
        import pickle
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
    parser.add_argument('--generations', type=int, default=50, help='Generations to run')
    
    args = parser.parse_args()
    trainer = Trainer(args)
    trainer.run()

if __name__ == '__main__':
    # On Windows/MacOS, multiprocessing might need this. On Linux it's usually fine.
    main()
