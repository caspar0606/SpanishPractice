from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from src.llm.input import AgentInputs
from langchain.messages import SystemMessage, HumanMessage, AIMessage


def agent_run(agent_inputs: AgentInputs):
    model = create_model("placeholder")

    agent = create_agent(
        model=model,
        system_prompt=agent_inputs.system_prompt,
        response_format=agent_inputs.output_schema,
        name=agent_inputs.name
    )

    response = agent.invoke({"messages": [HumanMessage(f"{agent_inputs.lesson_topics}, if None, Ignore."), 
                                          HumanMessage(f"{agent_inputs.input_text}, if None, Ingore")]})
    
    return response

def create_model(model_inputs: str):
    return init_chat_model(model = "gpt-5.4-mini")
