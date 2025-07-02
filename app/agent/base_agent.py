from datetime import date
from typing import Annotated, Sequence, Type, Dict, Optional, TypedDict
from langchain_core.messages import SystemMessage, BaseMessage
from langchain.prompts import PromptTemplate
from langgraph.checkpoint.base import Checkpoint
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from app.agent.abstract_agent import AbstractAgent, AgentState
from app.agent.clients import AzureChatOpenAI, azure_openai_client
from app.db import AsyncPostgresPool


# NOTE: Use litellm to make it platform agnostic


class BaseAgent(AbstractAgent):
    _instance: Dict[Type["BaseAgent"], "BaseAgent"] = {}
    _bypass_sigleton: bool = False
    """
    # Normal singleton usage
    agent1 = BaseAgent()

    # Force recreation (e.g., in tests)
    BaseAgent.reset_instance()
    agent2 = BaseAgent()  # New instance

    # Temporary bypass of singleton
    BaseAgent.set_bypass_singleton(True)
    agent3 = BaseAgent()  # Always new instance while bypass is True
    BaseAgent.set_bypass_singleton(False)
    """

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super().__new__(cls)
        return cls._instance[cls]

    def __init__(
        self,
        client: Optional[AzureChatOpenAI] = None,
        memory: Optional[Checkpoint] = None,
        tools: Optional[list] = None,
        prompt_template: Optional[PromptTemplate] = None,
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.client = client or azure_openai_client
        self.tools = tools or self.get_tools()
        self.prompt_template = prompt_template or self.get_prompt_template()
        self.client_with_tool = self.client.bind_tools(
            tools=self.tools, tool_choice="auto"
        )
        self.app = None
        self.memory = memory
        self._initialized: bool = True

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance - allows force reinitialization."""
        if cls in cls._instance:
            del cls._instance[cls]

    @classmethod
    def set_bypass_singleton(cls, state: bool):
        """Enable or disable singleton behavior"""
        cls._bypass_sigleton = state

    @property
    def AgentState(self) -> Type[AgentState]:
        class DefaultState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        return DefaultState

    async def llm_node(
        self, agent_state: AbstractAgent.AgentState
    ) -> AbstractAgent.AgentState:
        system_prompt = SystemMessage(
            content=await self.get_prompt_template().aformat(
                current_date=date.today().isoformat()
            )
        )
        agent_state["messages"] = [system_prompt] + agent_state["messages"]
        response = await self.client_with_tool.ainvoke(agent_state["messages"])
        return {"messages": [response]}

    def should_continue(self, agent_state: AbstractAgent.AgentState) -> str:
        last_message = agent_state["messages"][-1]
        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            return "continue"
        return "end"

    async def delete_thread_data(self, thread_id: str):
        pool = await AsyncPostgresPool.get_pool()
        async with pool.connection() as connection:
            memory = AsyncPostgresSaver(conn=connection)
            await memory.adelete_thread(thread_id=thread_id)

    async def build_graph(self):
        if not self.memory:
            raise RuntimeError("This Agent requires memory, but None was provided")
        tool_node = ToolNode(tools=self.tools)
        graph = StateGraph(self.AgentState)
        graph.add_node("llm", self.llm_node)
        graph.add_node("tools", tool_node)

        graph.add_edge(START, "llm")
        graph.add_conditional_edges(
            "llm", self.should_continue, {"continue": "tools", "end": END}
        )
        graph.add_edge("tools", "llm")
        self.app = graph.compile(checkpointer=self.memory)
