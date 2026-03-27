from langchain.chat_models import init_chat_model

w_prompting_model = init_chat_model(
    model="gpt-5.4-mini",
    temperature = 0.5
    )


w_marking_model = init_chat_model(
    model="gpt-5.4-mini",
    temperature = 0
    )