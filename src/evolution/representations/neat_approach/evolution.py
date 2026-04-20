import neat
from src.evolution.base import BaseEvolution
from .genome import NEATGenome

class NEATEvolution(BaseEvolution):
    """
    Implementation of the NEAT algorithm approach.
    """
    def __init__(self, config_path):
        self.config = neat.Config(
            neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation,
            config_path
        )
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population.add_reporter(self.stats)

    def evaluate_generation(self, genomes, fitness_fn):
        """
        In NEAT-python, evaluation is typically done inside pop.run(eval_genomes).
        This method will wrap that behavior.
        """
        def eval_wrapper(neat_genomes, config):
            for genome_id, genome in neat_genomes:
                wrapped = NEATGenome(genome, config)
                genome.fitness = fitness_fn(wrapped)

        self.population.run(eval_wrapper, 1)

    def select_best(self, genomes=None):
        """Returns the best genome from the population."""
        return self.population.best_genome
