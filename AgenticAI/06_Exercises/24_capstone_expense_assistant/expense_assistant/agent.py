"""Milestone 5 · The agent  (revise: steps 10, 11, 12)

Goal: ``create_agent`` with our tools. Memory comes from a checkpointer + ``thread_id``.
Check: pytest tests/test_m5_agent.py
"""

from datetime import date  # noqa: F401

from langchain.agents import create_agent  # noqa: F401
from langchain.messages import HumanMessage  # noqa: F401
from langchain_core.language_models import BaseChatModel

from .models import get_model  # noqa: F401
from .tools import ALL_TOOLS  # noqa: F401

# TODO (M5): write the system prompt. Include "Today is {today}." and tell the agent
#   when to use each tool (and to never guess numbers; use the tools instead).
SYSTEM_PROMPT = "You are a helpful expense-tracker assistant. Today is {today}."


def build_agent(model: BaseChatModel | None = None, *, tools=None, checkpointer=None, middleware=None):
    """Create the expense agent.

    Args:
        model: Chat model; defaults to ``get_model()``.
        tools: Tools the agent may use; defaults to ``ALL_TOOLS``.
        checkpointer: e.g. ``InMemorySaver()`` for memory. ``None`` = no memory.
        middleware: List of middleware (Milestone 6); default none.

    TODO (M5): return ``create_agent(...)``. Fill ``{today}`` in SYSTEM_PROMPT with ``.format``.
      Careful: ``tools=[]`` is a valid choice, so test ``tools is None``, not ``not tools``.
    """
    raise NotImplementedError("M5: implement build_agent")


def ask(agent, question: str, thread_id: str) -> str:
    """Send one message in a conversation thread and return the agent's final reply text.

    TODO (M5): invoke with ``{"messages": [HumanMessage(question)]}`` and
      ``{"configurable": {"thread_id": thread_id}}``; return the last message's content.
    """
    raise NotImplementedError("M5: implement ask")
