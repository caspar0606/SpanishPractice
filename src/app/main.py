from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from src.application.services.reading import reading_mode_run
from src.application.services.writing import writing_mode_run
from src.infrastructure.persistence.file_storage import save_user_state
from src.domain.enums import ExerciseTypes
from src.infrastructure.persistence.session_storage import store_session, update_progress
from src.infrastructure.cli.user import user_selection
from src.app.score import show_user_progress
from src.application.exercise_selection import exercise_selection, initialise_session



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
        user.history.append(store_session(current_session, user))
        user.progress_history.extend(current_session.progress_history)
        user.first_time = False
        save_user_state(user)
        break

    elif user_continue == "yes":
        continue



        

