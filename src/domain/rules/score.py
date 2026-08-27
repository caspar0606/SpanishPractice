from src.domain.models.progress import ComputeStats, Progress


# Calculates user score as a percentage of correct attempts over total attempts
def calculate_score(compute_stats: ComputeStats) -> float:
    if compute_stats.total_attempts == 0:
        return 0
    return (compute_stats.correct_attempts / compute_stats.total_attempts) * 100

# Adds two ComputeStats objects together to combine their total and correct attempts
def add_scores(compute_stats1: ComputeStats, compute_stats2: ComputeStats) -> None:
    compute_stats1.total_attempts += compute_stats2.total_attempts
    compute_stats1.correct_attempts += compute_stats2.correct_attempts

# Folds one exercise's scores into the running total. Iterates the exercise because a
# marking agent only reports the areas it actually saw, so its dicts are usually partial;
# areas absent from the exercise keep their existing total untouched.
def combine_scores(progress: Progress, exercise: Progress):
    for category in ["tenses", "grammar", "topics"]:
        prog_dict = getattr(progress, category)
        ex_dict = getattr(exercise, category)

        for key, exercise_stats in ex_dict.items():
            if key not in prog_dict:
                prog_dict[key] = ComputeStats()
            add_scores(prog_dict[key], exercise_stats)
