from datetime import date
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from langfuse import observe

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.db import AsyncPostgresPool
from app.core import settings
from app.agent.murshid.prompt import AGENT_MURSHID_PROMPT_TEMPLATE
from app.agent.murshid.tools import similarity_search

azure_openai_client = AzureChatOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_GPT4o_VERSION,
    azure_deployment="gpt-4o-mini",
    temperature=0.7,
)


class AgentMurshid:
    _instance = None

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgentMurshid, cls).__new__(cls)
        return cls._instance

    def __init__(self, client: AzureChatOpenAI = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.client = client or azure_openai_client
        self.tools = [similarity_search]
        self.app = None
        self._initialized = True

    async def llm_node(self, agent_state: AgentState) -> AgentState:
        system_prompt = SystemMessage(
            content=await AGENT_MURSHID_PROMPT_TEMPLATE.aformat(
                current_date=date.today().isoformat(),
            )
        )
        agent_state["messages"] = [system_prompt] + agent_state["messages"]

        response = await self.langfuse_invoke(agent_state["messages"])
        return {"messages": [response]}

    @observe(name="murshid-agent-invoke")
    async def langfuse_invoke(self, messages: Sequence[BaseMessage]) -> BaseMessage:
        return await self.client.ainvoke(messages)

    def should_continue(self, agent_state: AgentState) -> str:
        last_message = agent_state["messages"][-1]
        if getattr(last_message, "tool", None):
            return "continue"
        return "end"

    async def delete_thread_data(self, thread_id: str):
        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.adelete_thread(thread_id=thread_id)

    async def build_graph(self):
        tool_call = ToolNode(tools=self.tools)
        graph = StateGraph(self.AgentState)
        graph.add_node("llm", self.llm_node)
        graph.add_node("tools", tool_call)
        graph.add_edge(START, "llm")
        graph.add_conditional_edges(
            "llm",
            self.should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        graph.add_edge("tools", "llm")

        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.setup()
            self.app = graph.compile(checkpointer=memory)


# Factory
async def get_agent_murshid() -> AgentMurshid:
    agent_murshid = AgentMurshid()
    if agent_murshid.app is None:
        await agent_murshid.build_graph()
    return agent_murshid
