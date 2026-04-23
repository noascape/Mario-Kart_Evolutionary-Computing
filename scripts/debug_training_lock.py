import stable_retro as retro
import os
import cv2
import numpy as np
import neat
import pickle
import sys

project_root = '/workspaces/Mario-Kart_Evolutionary-Computing'
sys.path.insert(0, project_root)
from src.env.mario_kart_wrapper import MarioKartWrapper
from src.evolution.representations.neat_approach.genome import NEATGenome

def debug_run():
    custom_path = os.path.join(project_root, 'src/env/custom_integration')
    retro.data.add_custom_integration(custom_path)
    
    config_path = os.path.join(project_root, 'config/neat-feedforward.cfg')
    genome_path = os.path.join(project_root, 'best_genome.pkl')
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    with open(genome_path, 'rb') as f:
        genome = pickle.load(f)
    
    wrapped_genome = NEATGenome(genome, config)
    
    state_path = os.path.join(custom_path, 'SuperMarioKart-Snes-v0/start_race.state')
    env = retro.make(
        game='SuperMarioKart-Snes-v0', 
        state=state_path, 
        inttype=retro.data.Integrations.CONTRIB_ONLY, 
        render_mode='rgb_array'
    )
    env = MarioKartWrapper(env)
    
    obs, info = env.reset()
    
    print("Step | X | Y | Speed | Lap | CP | Stat | Buttons")
    for i in range(200):
        action = wrapped_genome.get_action({'obs': obs, 'ram_state': info})
        obs, reward, terminated, truncated, info = env.step(action)
        
        buttons = ["B", "Y", "SEL", "STA", "UP", "DO", "LE", "RI", "A", "X", "L", "R"]
        pressed = [buttons[j] for j, val in enumerate(action) if val > 0]
        
        if i % 20 == 0:
            print(f"{i:4} | {info['x']:4} | {info['y']:4} | {info['speed']:5} | {info['lap']:3} | {info['checkpoint']:2} | {info['status']:4} | {pressed}")
            
        if terminated or truncated:
            print(f"Terminated at step {i}!")
            break
            
    env.close()

if __name__ == "__main__":
    debug_run()
