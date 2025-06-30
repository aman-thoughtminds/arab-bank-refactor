from abc import ABC, abstractmethod
from typing import Annotated, TypedDict, Sequence, Type
from langchain.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class AbstractAgent(ABC):
    @abstractmethod
    def get_tools(self) -> list: ...

    @abstractmethod
    def get_prompt_template(self) -> PromptTemplate: ...

    # @abstractmethod
    # async def get_memory(self) -> BaseCheckpointSaver: ...
    @property
    @abstractmethod
    def AgentState(self) -> Type[AgentState]: ...
