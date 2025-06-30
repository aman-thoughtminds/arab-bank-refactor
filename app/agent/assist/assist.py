# AgentAssist
from langchain.prompts import PromptTemplate
from app.agent.base_agent import BaseAgent
from app.agent.assist.prompt import ASSIST_AGENT_PROMPT_TEMPLATE


class Assist(BaseAgent):
    def get_tools(self) -> list:
        return []

    def get_prompt_template(self) -> PromptTemplate:
        return ASSIST_AGENT_PROMPT_TEMPLATE
