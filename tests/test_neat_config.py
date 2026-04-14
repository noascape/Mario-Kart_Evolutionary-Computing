import neat
import os

def test_neat_config_load():
    """Test that the NEAT configuration can be loaded and population initialized."""
    config_path = 'config/neat-feedforward.cfg'
    assert os.path.exists(config_path), f"Config file '{config_path}' missing"
    
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    pop = neat.Population(config)
    assert len(pop.population) == 20, f"Expected population size 20, got {len(pop.population)}"
    
    # Check network dimensions
    assert config.genome_config.num_inputs == 4096
    assert config.genome_config.num_outputs == 12

if __name__ == "__main__":
    test_neat_config_load()
