from typing import List
from pydantic import BaseModel
from langchain_core.messages import BaseMessage


class MessagesResponse(BaseModel):
    messages: List[BaseMessage]
