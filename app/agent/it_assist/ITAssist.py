from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage


from langgraph.graph.message import add_messages

from app.agent.it_assist.prompt import ITAssistPromptTemplate
from app.agent.it_assist.tools import general_similarity_search
from app.agent.base_agent import BaseAgent


class ITAssist(BaseAgent):
    def get_tools(self) -> list:
        return [general_similarity_search]

    def get_prompt_template(self):
        return ITAssistPromptTemplate

    @property
    def AgentState(self):
        class ITAssist(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]

        return ITAssist
