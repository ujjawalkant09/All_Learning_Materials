"""Milestone 8 · cli.py — run: pytest tests/test_m8_cli.py"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver

from conftest import tool_call
from expense_assistant import db
from expense_assistant.agent import build_agent
from expense_assistant.cli import new_ai_replies, resolve_interrupts
from expense_assistant.middleware import build_middleware
from expense_assistant.schemas import Expense


def test_new_ai_replies_only_after_last_human_message():
    messages = [
        HumanMessage("old"), AIMessage("old reply"),
        HumanMessage("new"), tool_call("spending_summary"), ToolMessage("{}", tool_call_id="call_1"),
        AIMessage("answer"), AIMessage("⚠️ Budget alert"),
    ]
    assert new_ai_replies(messages) == ["answer", "⚠️ Budget alert"]


def _paused_delete(fake_model):
    expense_id = db.insert_expense(Expense(amount=100, category="food", description="pizza"))
    agent = build_agent(
        fake_model(tool_call("delete_expense", expense_id=expense_id), AIMessage("done")),
        checkpointer=InMemorySaver(), middleware=build_middleware(),
    )
    config = {"configurable": {"thread_id": "cli"}}
    result = agent.invoke({"messages": [{"role": "user", "content": "delete it"}]}, config)
    return agent, result, config


def test_resolve_interrupts_approve(fake_model):
    agent, result, config = _paused_delete(fake_model)
    questions = []
    final = resolve_interrupts(agent, result, config, decide=lambda q: questions.append(q) or "y")
    assert "__interrupt__" not in final
    assert "delete_expense" in questions[0]
    assert db.spending_by_category() == {}


def test_resolve_interrupts_reject(fake_model):
    agent, result, config = _paused_delete(fake_model)
    resolve_interrupts(agent, result, config, decide=lambda q: "n")
    assert db.spending_by_category() == {"food": 100}
