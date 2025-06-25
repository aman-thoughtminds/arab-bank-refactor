from typing import Any
from langchain_core.messages import HumanMessage
from app.agent.murshid import get_agent_murshid


async def generate_chat_response(
    user_query: str,
    thread_id: str,
) -> str | Any:
    agent_murshid = await get_agent_murshid()
    if agent_murshid.app:
        result = await agent_murshid.app.ainvoke(
            {
                "messages": [HumanMessage(content=user_query)],
            },
            config={"configurable": {"thread_id": thread_id}},
        )
        breakpoint()
        return result
