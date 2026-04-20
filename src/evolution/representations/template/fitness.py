def calculate_fitness(genome_result):
    """
    Template for representation-specific fitness calculations.
    genome_result: Dictionary containing progress, speed, collisions, etc.
    """
    progress = genome_result.get('progress', 0)
    speed = genome_result.get('avg_speed', 0)
    
    # Simple composite score
    return progress * 1.0 + speed * 0.1
