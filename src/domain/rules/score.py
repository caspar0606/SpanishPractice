
from src.domain.models.progress import ComputeStats, Progress
from src.domain.models.user import User


# Calculates user score as a percentage of correct attempts over total attempts
def calculate_score(compute_stats: ComputeStats) -> float:
    if compute_stats.total_attempts == 0:
        return 0
    return (compute_stats.correct_attempts / compute_stats.total_attempts) * 100

# Adds two ComputeStats objects together to combine their total and correct attempts
def add_scores(compute_stats1: ComputeStats, compute_stats2: ComputeStats) -> None:
    compute_stats1.total_attempts += compute_stats2.total_attempts
    compute_stats1.correct_attempts += compute_stats2.correct_attempts

def combine_scores(progress: Progress, exercise: Progress):
    for category in ["tenses", "grammar", "topics"]:
        prog_dict = getattr(progress, category)
        ex_dict = getattr(exercise, category)

        for key in prog_dict:
            add_scores(prog_dict[key], ex_dict[key])


def show_user_progress(user: User):
    from src.infrastructure.cli.display import print_big_lines, print_scores

    while True:
        print_big_lines()
        print_user_progress = input("Would you like to see your progress (yes/no)?:\n").strip().lower()

        if print_user_progress == "yes":
            print_scores(user.progress)
            break

        elif print_user_progress == "no":
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
