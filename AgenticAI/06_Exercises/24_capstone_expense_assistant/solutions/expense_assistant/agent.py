"""Milestone 5 · The agent  (revise: steps 10, 11, 12)

``create_agent`` runs the tool loop for us. Memory comes from a checkpointer + ``thread_id``.
"""

from datetime import date

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.language_models import BaseChatModel

from .models import get_model
from .tools import ALL_TOOLS

SYSTEM_PROMPT = (
    "You are a helpful expense-tracker assistant. Today is {today}.\n"
    "- Use add_expense when the user reports spending money.\n"
    "- Use spending_summary or query_expenses to answer questions about their spending; never guess numbers.\n"
    "- Use delete_expense only when the user explicitly asks to delete an expense.\n"
    "Amounts are in rupees. Keep answers short."
)


def build_agent(model: BaseChatModel | None = None, *, tools=None, checkpointer=None, middleware=None):
    """Create the expense agent.

    Args:
        model: Chat model; defaults to ``get_model()``.
        tools: Tools the agent may use; defaults to ``ALL_TOOLS``.
        checkpointer: e.g. ``InMemorySaver()`` for memory. ``None`` = no memory
            (used when the agent runs inside the LangGraph app, which owns memory).
        middleware: List of middleware (see ``middleware.build_middleware``).
    """
    return create_agent(
        model=model or get_model(),
        tools=ALL_TOOLS if tools is None else tools,
        system_prompt=SYSTEM_PROMPT.format(today=date.today().isoformat()),
        checkpointer=checkpointer,
        middleware=middleware or [],
    )


def ask(agent, question: str, thread_id: str) -> str:
    """Send one message in a conversation thread and return the agent's final reply."""
    result = agent.invoke({"messages": [HumanMessage(question)]}, {"configurable": {"thread_id": thread_id}})
    return result["messages"][-1].content
