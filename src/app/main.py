from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from src.domain.user import user_selection
from src.domain.enums import ExerciseTypes
from src.app.score import combine_scores, show_user_progress
from src.app.exercise_selection import exercise_selection, initialise_session
from src.mode.writing import writing_mode_run
from src.mode.reading import reading_mode_run


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
    finished_exercise 
    if (current_session.current_exercise.exercise_type is ExerciseTypes.WRITING):
        finished_exercise = writing_mode_run(current_session)
       



    elif(current_session.current_exercise.exercise_type is ExerciseTypes.READING):
        finished_exercise = reading_mode_run(current_session)

    current_session.history.append(finished_exercise)
    combine_scores(user.progress, finished_exercise.score)



        

