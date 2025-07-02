from app.agent.base_agent import BaseAgent
from app.agent.assist.prompt import ASSIST_AGENT_PROMPT_TEMPLATE
from app.agent.assist.tools import send_email
from langchain.prompts import PromptTemplate


class Assist(BaseAgent):
    def get_tools(self) -> list:
        return [send_email]

    def get_prompt_template(self) -> PromptTemplate:
        return ASSIST_AGENT_PROMPT_TEMPLATE
