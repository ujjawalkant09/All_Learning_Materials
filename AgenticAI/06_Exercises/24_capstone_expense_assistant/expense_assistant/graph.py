"""Milestone 7 · LangGraph app  (revise: steps 16, 17, 18)

Instead of sending everything to one agent, a router decides what to do:

    START → classify_intent ─┬─ log_expense      → END   (structured output, no agent needed)
                             ├─ answer_question  → END   (read-only agent)
                             └─ small_talk       → END   (plain model call)

The building blocks are passed in as arguments (dependency injection), so tests can use fakes.
Check: pytest tests/test_m7_graph.py
"""

import operator  # noqa: F401
from collections.abc import Callable
from typing import Annotated, Literal  # noqa: F401

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage  # noqa: F401
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph  # noqa: F401
from langgraph.graph.message import add_messages  # noqa: F401
from typing_extensions import TypedDict

from . import db  # noqa: F401
from .schemas import Expense, Intent


class AssistantState(TypedDict):
    """Graph state.

    TODO (M7): three keys:
      - messages:  list of messages, appended with the ``add_messages`` reducer
      - intent:    str, overwritten every turn (no reducer)
      - saved_ids: list[int], accumulated across turns with ``operator.add``
    """


def last_user_text(state: AssistantState) -> str:
    """Content of the most recent HumanMessage. (Given.)"""
    return next(m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage))


def build_graph(
    classify: Callable[[str], Intent],
    parse_expense: Callable[[str], Expense],
    agent,
    chat_model,
    checkpointer=None,
):
    """Wire the router graph.

    TODO (M7): define four nodes as inner functions. Each returns ONLY the keys it updates.
      - classify_intent: {"intent": classify(text).intent}
      - log_expense:     parse, db.insert_expense, reply with an AIMessage starting "Saved",
                         and return {"messages": [...], "saved_ids": [new_id]}
      - answer_question: agent.invoke({"messages": state["messages"]}) → return only its last message
      - small_talk:      chat_model.invoke([SystemMessage(...), *state["messages"]])
      plus a router ``route_by_intent(state) -> Literal[...]`` mapping
        "log_expense" → "log_expense", "question" → "answer_question", anything else → "small_talk".
      Edges: START → classify_intent → (conditional) → each node → END.
      Return ``builder.compile(checkpointer=checkpointer)``.
    """
    raise NotImplementedError("M7: implement build_graph")


def build_default_graph(checkpointer=None):
    """The real app: LLM-powered classifier, parser and a read-only agent. (Given; works once M1–M7 are done.)"""
    from .agent import build_agent
    from .models import get_model
    from .prompts import build_expense_parser, build_intent_classifier
    from .tools import READ_ONLY_TOOLS

    model = get_model()
    classifier = build_intent_classifier(model)
    parser = build_expense_parser(model)
    return build_graph(
        classify=lambda text: classifier.invoke({"text": text}),
        parse_expense=lambda text: parser.invoke({"text": text}),
        agent=build_agent(model, tools=READ_ONLY_TOOLS),
        chat_model=model,
        checkpointer=checkpointer or InMemorySaver(),
    )
