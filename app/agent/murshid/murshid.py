from datetime import date
from typing import Annotated, Sequence, TypedDict

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage


from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.db import AsyncPostgresPool
from app.core import settings
from app.agent.murshid.prompt import AGENT_MURSHID_PROMPT_TEMPLATE
from app.agent.murshid.tools import general_similarity_search
from app.utils.perf import timer


# Configure your base client (GPT-4o or GPT-4o-mini)
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
        self.tools = [general_similarity_search]

        # When tools are required
        self.client_with_tool = self.client.bind_tools(
            tools=self.tools, tool_choice="auto"
        )

        self.app = None
        self._initialized = True

    @timer
    async def llm_node(self, agent_state: AgentState) -> AgentState:
        system_prompt = SystemMessage(
            content=await AGENT_MURSHID_PROMPT_TEMPLATE.aformat(
                current_date=date.today().isoformat(),
            )
        )

        agent_state["messages"] = [system_prompt] + agent_state["messages"]

        response = await self.client_with_tool.ainvoke(agent_state["messages"])
        # print(f"LLM response: {response}")
        return {"messages": [response]}

    # @observe(name="murshid-agent-invoke")
    # async def langfuse_invoke(self, messages: Sequence[BaseMessage]) -> BaseMessage:
    #     return await self.client.ainvoke(messages)

    @timer
    def should_continue(self, agent_state: AgentState) -> str:
        last_message = agent_state["messages"][-1]
        # print("Last message:", last_message)

        # if isinstance(last_message, AIMessage) and getattr(
        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            # last_message, "tool_calls", None
            # ):
            return "continue"
        return "end"

    async def delete_thread_data(self, thread_id: str):
        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.adelete_thread(thread_id=thread_id)

    @timer
    async def build_graph(self):
        # Step 1: Define the tool execution node
        tool_node = ToolNode(tools=self.tools)

        # Step 2: Define the state graph
        graph = StateGraph(self.AgentState)

        # Step 3: Register nodes
        graph.add_node("llm", self.llm_node)
        graph.add_node("tools", tool_node)

        # Step 4: Add flow edges
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

        # Step 5: Register checkpointing
        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.setup()
            self.app = graph.compile(checkpointer=memory)


# Factory function
@timer
async def get_agent_murshid() -> AgentMurshid:
    agent_murshid = AgentMurshid()
    if agent_murshid.app is None:
        await agent_murshid.build_graph()
    return agent_murshid
