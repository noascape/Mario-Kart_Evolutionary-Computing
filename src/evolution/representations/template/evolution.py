from src.evolution.base import BaseEvolution
from .genome import TemplateGenome

class TemplateEvolution(BaseEvolution):
    """
    Standard template for evolutionary logic (Selection, Speciation, etc.)
    """
    def evaluate_generation(self, genomes, fitness_fn):
        """
        Evaluates a list of genomes using the provided fitness function.
        """
        for genome in genomes:
            fitness = fitness_fn(genome)
            genome.fitness = fitness

    def select_best(self, genomes):
        """Sorts and returns the best genomes."""
        return sorted(genomes, key=lambda x: x.fitness, reverse=True)[:self.config['elitism_count']]
