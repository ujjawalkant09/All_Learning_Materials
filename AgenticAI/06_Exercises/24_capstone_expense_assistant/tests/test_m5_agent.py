"""Milestone 5 · agent.py — run: pytest tests/test_m5_agent.py"""

from langgraph.checkpoint.memory import InMemorySaver

from conftest import tool_call
from langchain_core.messages import AIMessage

from expense_assistant import db
from expense_assistant.agent import ask, build_agent
from expense_assistant.tools import READ_ONLY_TOOLS


def test_agent_runs_the_add_expense_tool(fake_model):
    model = fake_model(
        tool_call("add_expense", amount=250, category="food", description="pizza"),
        AIMessage("Saved your pizza!"),
    )
    agent = build_agent(model)
    result = agent.invoke({"messages": [{"role": "user", "content": "I spent 250 on pizza"}]})

    assert result["messages"][-1].content == "Saved your pizza!"
    assert db.spending_by_category() == {"food": 250}


def test_memory_is_per_thread(fake_model):
    agent = build_agent(fake_model(AIMessage("a"), AIMessage("b"), AIMessage("c")), checkpointer=InMemorySaver())
    ask(agent, "hello", "thread-1")
    ask(agent, "again", "thread-1")
    ask(agent, "hi", "thread-2")

    assert len(agent.get_state({"configurable": {"thread_id": "thread-1"}}).values["messages"]) == 4
    assert len(agent.get_state({"configurable": {"thread_id": "thread-2"}}).values["messages"]) == 2


def test_ask_returns_final_text(fake_model):
    agent = build_agent(fake_model(AIMessage("Hello!")), checkpointer=InMemorySaver())
    assert ask(agent, "hi", "t") == "Hello!"


def test_tools_can_be_restricted(fake_model):
    agent = build_agent(fake_model(AIMessage("ok")), tools=READ_ONLY_TOOLS)
    assert set(agent.nodes["tools"].bound.tools_by_name) == {"query_expenses", "spending_summary"}
