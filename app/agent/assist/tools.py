import smtplib
from typing import Annotated
from email.message import EmailMessage
from typing import List, Optional
from pydantic import BaseModel
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from app.core.config import settings


class SendEmailInput(BaseModel):
    subject: str
    body: str
    to: List[str]
    sender: str
    smtp_server: str = settings.SMTP_SERVER
    smtp_port: int = settings.SMTP_PORT
    username: str = settings.SMTP_USERNAME
    password: str = settings.SMTP_PASSWORD
    html_body: Optional[str]


@tool
async def send_email(
    input: SendEmailInput,
    agent_state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Sends an email using SMTP.

    Args:
        input: Email parameters including subject, body, recipients, SMTP credentials, etc.
        agent_state: Current agent state injected automatically.
        tool_call_id: Tool call ID used for tracing this operation.

    Returns:
        Command: Updated agent state with success or error message.
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = input.subject
        msg["From"] = input.sender
        msg["To"] = ", ".join(input.to)
        msg.set_content(input.body)

        if input.html_body:
            msg.add_alternative(input.html_body, subtype="html")

        with smtplib.SMTP(input.smtp_server, input.smtp_port) as server:
            server.starttls()
            server.login(input.username, input.password)
            server.send_message(msg)

        agent_state["messages"] = [
            ToolMessage(
                content="Email sent successfully.",
                tool_call_id=tool_call_id,
            )
        ]
        return Command(update=agent_state)

    except Exception as e:
        agent_state["messages"] = [
            ToolMessage(
                content=f"Failed to send email: {str(e)}",
                tool_call_id=tool_call_id,
            )
        ]
        return Command(update=agent_state)
