from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from src.core.user import user_selection
from src.domain.classes import CurrentSession
from src.domain.enums import ExerciseTypes
from src.app.score import show_user_progress
from src.app.exercise_selection import exercise_selection
from src.llm.models import w_prompting_model
from src.llm.prompts import w_prompting_system_prompt
from src.llm.llm_classes import prompt_formatter



#User Selection
user = user_selection()

#Session Initialisation
current_session = CurrentSession(
    user=user)


#### User Progress ####
show_user_progress(user)

#### User Exercise Selection ####
exercise = exercise_selection(current_session)

current_session.current_exercise = exercise

#### User Exercise Focus ####

llmprompt = prompt_formatter(current_session.current_exercise)

if (exercise.exercise_type is ExerciseTypes.WRITING):
    writing_prompt = w_prompting_model.invoke([
        f"SystemMessage: {w_prompting_system_prompt}"
        f"HumanMessage: {llmprompt}"])
    print(writing_prompt)

    

