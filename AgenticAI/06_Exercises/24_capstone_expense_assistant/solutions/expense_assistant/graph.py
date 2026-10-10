"""Milestone 7 · LangGraph app  (revise: steps 16, 17, 18)

Instead of sending everything to one agent, a router decides what to do:

    START → classify_intent ─┬─ log_expense      → END   (structured output, no agent needed)
                             ├─ answer_question  → END   (read-only agent)
                             └─ small_talk       → END   (plain model call)

The building blocks are passed in as arguments (dependency injection), so tests can use fakes.
"""

import operator
from collections.abc import Callable
from typing import Annotated, Literal

from langchain.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from . import db
from .schemas import Expense, Intent


class AssistantState(TypedDict):
    """Graph state.

    messages:  chat history; ``add_messages`` appends.
    intent:    set by the classifier; no reducer, so it is overwritten every turn.
    saved_ids: ids of expenses saved in this thread; ``operator.add`` accumulates them.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    saved_ids: Annotated[list[int], operator.add]


def last_user_text(state: AssistantState) -> str:
    """Content of the most recent HumanMessage."""
    return next(m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage))


def build_graph(
    classify: Callable[[str], Intent],
    parse_expense: Callable[[str], Expense],
    agent,
    chat_model,
    checkpointer=None,
):
    """Wire the router graph.

    Args:
        classify: text -> ``Intent``.
        parse_expense: text -> ``Expense``.
        agent: an agent whose ``invoke({"messages": ...})`` answers spending questions.
        chat_model: a chat model for small talk.
        checkpointer: memory for the whole graph.
    """

    def classify_intent(state: AssistantState) -> dict:
        return {"intent": classify(last_user_text(state)).intent}

    def log_expense(state: AssistantState) -> dict:
        expense = parse_expense(last_user_text(state))
        expense_id = db.insert_expense(expense)
        reply = f"Saved #{expense_id}: {expense.amount:.2f} for {expense.description} ({expense.category}) on {expense.spent_on}"
        return {"messages": [AIMessage(reply)], "saved_ids": [expense_id]}

    def answer_question(state: AssistantState) -> dict:
        result = agent.invoke({"messages": state["messages"]})
        return {"messages": [result["messages"][-1]]}

    def small_talk(state: AssistantState) -> dict:
        system = SystemMessage("You are a friendly expense-tracker assistant. Keep replies short.")
        return {"messages": [chat_model.invoke([system, *state["messages"]])]}

    def route_by_intent(state: AssistantState) -> Literal["log_expense", "answer_question", "small_talk"]:
        return {"log_expense": "log_expense", "question": "answer_question"}.get(state["intent"], "small_talk")

    builder = StateGraph(AssistantState)
    builder.add_node("classify_intent", classify_intent)
    builder.add_node("log_expense", log_expense)
    builder.add_node("answer_question", answer_question)
    builder.add_node("small_talk", small_talk)

    builder.add_edge(START, "classify_intent")
    builder.add_conditional_edges("classify_intent", route_by_intent)
    for node in ("log_expense", "answer_question", "small_talk"):
        builder.add_edge(node, END)

    return builder.compile(checkpointer=checkpointer)


def build_default_graph(checkpointer=None):
    """The real app: LLM-powered classifier, parser and a **read-only** agent (least privilege)."""
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
