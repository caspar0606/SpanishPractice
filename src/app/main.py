from datetime import datetime

from src.core.user import create_user, weak_areas, print_big_lines, print_small_lines
from src.domain.classes import CurrentSession, Exercise
from src.core.storage import create_new_user_file, load_user_state, save_user_state
from src.domain.enums import Grammar, Tenses, Topics, ExerciseTypes, DifficultyLevels
from src.domain.preferences import grammar_preferences, tense_preferences, topic_preferences, TENSE_PREFERENCES_CONFIG, GRAMMAR_PREFERENCES_CONFIG, TOPIC_PREFERENCES_CONFIG
from src.app.score import print_scores
from src.domain.classes import Exercise


#### User Selection ####
while True:
    response = input("Are you a new user (yes/no)?: ").strip().lower()

    if response == "yes": # Creates a new user and saves it as a json file in the userdata directory
        user = create_user(input("Enter your new username: ").strip().lower())
        if create_new_user_file(user.name) == 1: # Checks if User already exists
            continue
        save_user_state(user)
        break
    
    elif response == "no": # Loads user data
        user = load_user_state(input("Welcome back! Please enter your username: ").strip().lower())
        if user == None: # Checks if User exists
            continue
        break
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")

current_session = CurrentSession(
    user=user)


#### User Progress ####
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


#### User Exercise Selection ####
current_exercise = Exercise(
    start_time=datetime.now())

current_session.current_exercise = current_exercise 

while True:
    print_big_lines()
    exercise_type = input("Choose an exercise type (writing/reading): ").strip().lower()
    if exercise_type == "writing":
        current_session.current_exercise.exercise_type = ExerciseTypes.WRITING
        break
    elif exercise_type == "reading":
        current_session.current_exercise.exercise_type = ExerciseTypes.READING
        break
    else:
        print("Invalid exercise type. please select either writing or reading.")


#### User Exercise Focus ####
while True:
    print_big_lines()
    weak_or_preferences = input("Do you want to focus on weak areas or your preferences (weak/preferences)?: ").strip().lower()

    if weak_or_preferences == "weak":

        while True:
            print_big_lines()
            difficulty_level = input("Choose a difficulty level (beginner/novice/intermediate): ").strip().lower()

            # Sets exercise difficulty level based on user input using Enums
            for difficulty in DifficultyLevels: 
                if difficulty.value == difficulty_level:
                    current_session.current_exercise.difficulty_level = difficulty
                    break
            
            else:
                print("Invalid difficulty level. choose either 'beginner', 'novice', or 'intermediate'.")

            # Assigns focus areas based on weakest areas determined by the weak_areas function 
            current_session.current_exercise.focus_tenses, \
            current_session.current_exercise.focus_grammar, \
            current_session.current_exercise.focus_topics = weak_areas(current_session)
            break
        break

    elif weak_or_preferences == "preferences":

        # Gets user preferences and assigns them to focus areas
        while True:
            print_small_lines()
            if (focus_tenses := tense_preferences(input(f"Enter tense preferences: "
                                                    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRESENTE_DE_INDICATIVO]} for presente de indicativo"
                                                    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_IMPERFECTO]} for preterito imperfecto " 
                                                    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.PRETERITO_PERFECTO_SIMPLE]} for preterito perfecto simple" 
                                                    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.FUTURO_SIMPLE]} for futuro simple " 
                                                    f"\n{TENSE_PREFERENCES_CONFIG[Tenses.CONDICIONAL_SIMPLE]} for condicional simple"
                                                    "\n: ").strip())) is None:
                continue
            print_small_lines()
            if (focus_grammar := grammar_preferences(input(f"Enter grammar preferences: "
                                                        f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.GENDER_AGREEMENT]} for gender agreement"
                                                        f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.PLURALITY_AGREEMENT]} for plurality agreement"
                                                        f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.POR_PARA_USAGE]} for por/para usage"
                                                        f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.INDIRECT_DIRECT_PRONOUN_USAGE]} for indirect/direct pronoun usage"
                                                        f"\n{GRAMMAR_PREFERENCES_CONFIG[Grammar.VERB_SUBJECT_CONJUGATION]} for verb-subject conjugation"
                                                        "\n: ").strip())) is None:
                continue    
                    
            print_small_lines()
            if (focus_topics := topic_preferences(input(f"Enter topic preferences: " 
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.TRAVEL]} for travel "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.SCHOOL]} for school "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.WORK]} for work "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CULTURE]} for culture "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.CURRENT_EVENTS]} for current events "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.EMOTIONS]} for emotions "
                                                    f"\n{TOPIC_PREFERENCES_CONFIG[Topics.RELATIONSHIPS]} for relationships"
                                                    "\n: ").strip())) is None:
                continue

            current_session.current_exercise.focus_tenses = focus_tenses
            current_session.current_exercise.focus_grammar = focus_grammar
            current_session.current_exercise.focus_topics = focus_topics
            break
        break
    else:
        print("Invalid choice. Please enter 'weak' or 'preferences'.")