"""Milestone 7 · graph.py — run: pytest tests/test_m7_graph.py"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from expense_assistant import db
from expense_assistant.graph import build_graph
from expense_assistant.schemas import Expense, Intent


class FakeAgent:
    """Stands in for the read-only agent; records what it was asked."""

    def __init__(self):
        self.calls = []

    def invoke(self, state):
        self.calls.append(state)
        return {"messages": [*state["messages"], AIMessage("You spent 250 on food.")]}


class FakeChat:
    def invoke(self, messages):
        return AIMessage("Hello! How can I help with your expenses?")


def make_graph(intent: str):
    agent = FakeAgent()
    graph = build_graph(
        classify=lambda text: Intent(intent=intent, reason="test"),
        parse_expense=lambda text: Expense(amount=250, category="food", description="pizza"),
        agent=agent,
        chat_model=FakeChat(),
        checkpointer=InMemorySaver(),
    )
    return graph, agent


def run(graph, text, thread="t"):
    return graph.invoke({"messages": [HumanMessage(text)]}, {"configurable": {"thread_id": thread}})


def test_graph_has_the_expected_nodes():
    graph, _ = make_graph("chat")
    assert {"classify_intent", "log_expense", "answer_question", "small_talk"} <= set(graph.nodes)


def test_log_expense_route_saves_without_agent():
    graph, agent = make_graph("log_expense")
    state = run(graph, "I spent 250 on pizza")
    assert state["intent"] == "log_expense"
    assert db.spending_by_category() == {"food": 250}
    assert state["saved_ids"] and "Saved" in state["messages"][-1].content
    assert agent.calls == []


def test_saved_ids_accumulate_across_turns():
    graph, _ = make_graph("log_expense")
    run(graph, "pizza 250")
    state = run(graph, "pizza 250 again")
    assert len(state["saved_ids"]) == 2
    assert len(state["messages"]) == 4


def test_question_route_uses_agent():
    graph, agent = make_graph("question")
    state = run(graph, "how much on food?")
    assert len(agent.calls) == 1
    assert state["messages"][-1].content == "You spent 250 on food."


def test_chat_route_uses_plain_model():
    graph, agent = make_graph("chat")
    assert run(graph, "hi")["messages"][-1].content.startswith("Hello!")
    assert agent.calls == []
