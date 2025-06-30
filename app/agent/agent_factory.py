"""
factory for creating agents.
"""

from typing import Dict, Type

from app.agent.it_assist import ITAssist
from app.agent.assist import Assist
from app.agent.base_agent import BaseAgent

# TODO: implement strategy pattern for memory?
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.db import AsyncPostgresPool


_AGENT_CLASSES: Dict[str, Type[BaseAgent]] = {
    "it_assist": ITAssist,
    "assist": Assist,
}

_agent_instance: Dict[str, BaseAgent] = {}


async def get_agent(agent_name: str) -> BaseAgent:
    agent_name = agent_name.lower()

    if agent_name not in _AGENT_CLASSES:
        raise ValueError(f"Unknow agent {agent_name}")

    if agent_name not in _agent_instance:
        # Inject memory
        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.setup()
        agent_class = _AGENT_CLASSES[agent_name]
        agent = agent_class(memory=memory)  # TODO<amanb>:

        if agent.app is None:
            await agent.build_graph()
        _agent_instance[agent_name] = agent
    return _agent_instance[agent_name]
