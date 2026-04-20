import argparse
import neat
import os
import sys
import pickle
import numpy as np
import cv2

# Ensure the root of the project is in the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Ensure retro is available
try:
    import stable_retro as retro
except ImportError:
    import retro

from src.env.mario_kart_wrapper import MarioKartWrapper
from src.evolution.representations.neat_approach.genome import NEATGenome

# Register custom integration
custom_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration'))
retro.data.add_custom_integration(custom_path)

def main():
    parser = argparse.ArgumentParser(description='Run a trained NEAT genome in Super Mario Kart')
    parser.add_argument('--genome', type=str, default='best_genome.pkl', help='Path to the best genome pickle file')
    parser.add_argument('--config', type=str, default='config/neat-feedforward.cfg', help='Path to NEAT config')
    parser.add_argument('--steps', type=int, default=1000, help='Number of steps to run')
    parser.add_argument('--render', action='store_true', help='Attempt to render (requires X server)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.genome):
        print(f"Genome file '{args.genome}' not found.")
        return

    config_path = os.path.abspath(args.config)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    with open(args.genome, 'rb') as f:
        genome = pickle.load(f)
    
    wrapped_genome = NEATGenome(genome, config)
    
    # NEW: Ensure screenshots directory exists
    screenshot_dir = os.path.join(project_root, 'Gameplay/screenshots')
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    render_mode = 'human' if args.render else 'rgb_array'
    try:
        # Load the absolute path to the start state
        state_path = os.path.abspath(os.path.join(project_root, 'src/env/custom_integration/SuperMarioKart-Snes-v0/start_race.state'))
        inner_env = retro.make(
            game='SuperMarioKart-Snes-v0', 
            state=state_path, 
            inttype=retro.data.Integrations.CONTRIB_ONLY, 
            render_mode=render_mode
        )
        env = MarioKartWrapper(inner_env)
    except Exception as e:
        print(f"Error making env: {e}")
        return
        
    obs, info = env.reset()
    
    print(f"Starting run for {args.steps} steps...")
    for i in range(args.steps):
        action = wrapped_genome.get_action({'obs': obs, 'ram_state': info})
        obs, reward, terminated, truncated, info = env.step(action)
        
        if args.render:
            env.render()
        
        # Save frames if not rendering humanly, to see what happened
        if not args.render and i % 50 == 0:
            frame_bgr = cv2.cvtColor(obs, cv2.COLOR_RGB2BGR)
            fname = os.path.join(screenshot_dir, f"enjoy_frame_{i}.png")
            cv2.imwrite(fname, frame_bgr)
            print(f"Saved frame {i} to {fname}")

        if terminated or truncated:
            print("Environment terminated.")
            break
            
    env.close()
    print("Run complete.")

if __name__ == '__main__':
    main()
