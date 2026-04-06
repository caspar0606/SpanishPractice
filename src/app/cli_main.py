from dotenv import load_dotenv
import os

from src.domain.rules.score import show_user_progress
from src.infrastructure.cli.exercise_selection import initialise_session, exercise_selection
from src.application.services.reading import reading_mode_run
from src.application.services.writing import writing_mode_run
from src.infrastructure.persistence.file_storage import create_new_user_file, load_user_state, save_user_state
from src.domain.enums import ExerciseTypes
from src.infrastructure.persistence.session_storage import store_exercise, store_session, update_progress
from src.application.user import create_user

def user_selection():
    while True:
        response = input("Are you a new user (yes/no)?: ").strip().lower()

        if response == "yes": # Creates a new user and saves it as a json file in the userdata directory
            user = create_user(input("Enter your new username: ").strip().lower())
            if create_new_user_file(user.name) == 1: # Checks if User already exists
                continue

            save_user_state(user)
            return user
        
        elif response == "no": # Loads user data
            user = load_user_state(input("Welcome back! Please enter your username: ").strip().lower())

            if user == None: # Checks if User exists
                continue
            return user
        
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

#User Selection
user = user_selection()

#Session Initialisation
current_session = initialise_session(user)

while True:
    #User Progress
    show_user_progress(user)

    #User Exercise Selection
    current_session.current_exercise = exercise_selection(current_session)

    #User Exercise Execution 
    if (current_session.current_exercise.exercise_type is ExerciseTypes.WRITING):
        finished_exercise = writing_mode_run(current_session)

    #elif(current_session.current_exercise.exercise_type is ExerciseTypes.DRILLS):
        #finished_exercise = drills_mode_run(current_session)
        #pass

    else: #(current_session.current_exercise.exercise_type is ExerciseTypes.READING):
        finished_exercise = reading_mode_run(current_session)

    

    current_session.exercise_history.append(finished_exercise)
    current_session.progress_history.append(update_progress(user, finished_exercise))

    if (user_continue := input("Would you like to do another exercise? (yes/no): ")) == "no":
        #user.history.append(store_exercise(current_session.current_exercise, user))
        user.progress_history.extend(current_session.progress_history)
        user.first_time = False
        save_user_state(user)
        break

    elif user_continue == "yes":
        continue




        

