from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


from src.core.user import user_selection
from src.domain.classes import CurrentSession
from src.domain.enums import ExerciseTypes
from src.app.score import show_user_progress
from src.app.exercise_selection import exercise_selection, initialise_session
from src.mode.writing import writing_mode_run
from src.mode.reading import reading_mode_run


#User Selection
user = user_selection()

#Session Initialisation
current_session = initialise_session(user)

#User Progress
show_user_progress(user)

#User Exercise Selection
current_session.current_exercise = exercise_selection(current_session)

#User Exercise Execution 
if (current_session.current_exercise.exercise_type is ExerciseTypes.WRITING):
    writing_mode_run(current_session)
    

elif(current_session.current_exercise.exercise_type is ExerciseTypes.READING):
    reading_mode_run(current_session)

