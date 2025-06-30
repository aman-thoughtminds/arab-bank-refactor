from typing import Any
import asyncio
from langchain_core.messages import HumanMessage
from app.agent.agent_factory import get_agent


async def generate_chat_response(
    user_query: str, thread_id: str, agent_name: str = "it_assist"
) -> Any:
    agent = await get_agent(agent_name)
    response = await asyncio.wait_for(
        agent.app.ainvoke(
            {"messages": [HumanMessage(content=user_query)]},
            config={"configurable": {"thread_id": thread_id}},
        ),
        timeout=30,  # seconds
    )

    return response


async def generate_assit_agent_response(
    user_query: str,
    thread_id: str,
) -> dict | Any:
    """interface for assist agent. This will help you send email"""
    pass
