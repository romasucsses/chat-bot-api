from langchain_core.messages import HumanMessage
from .config import agent_executor


async def chat_bot(user_message: str, user_id: int):
    input_message = HumanMessage(content=user_message)
    config = {"configurable": {"thread_id": f"g34hqq45pjf8m_user{user_id}"}}

    full_response = ""
    for chunk in agent_executor.stream(
        {"messages": [input_message]}, config):
        full_response += chunk

    return full_response
