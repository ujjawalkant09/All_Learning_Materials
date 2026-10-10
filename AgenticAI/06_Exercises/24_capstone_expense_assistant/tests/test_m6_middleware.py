"""Milestone 6 · middleware.py — run: pytest tests/test_m6_middleware.py"""

from datetime import date

from langchain.agents.middleware import HumanInTheLoopMiddleware, PIIMiddleware, SummarizationMiddleware
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from conftest import tool_call
from expense_assistant import db
from expense_assistant.agent import build_agent
from expense_assistant.middleware import BudgetWarningMiddleware, CallLogMiddleware, build_middleware
from expense_assistant.schemas import Expense

CONFIG = {"configurable": {"thread_id": "t"}}


def test_build_middleware_contains_everything():
    kinds = [type(m) for m in build_middleware()]
    for expected in (CallLogMiddleware, SummarizationMiddleware, PIIMiddleware,
                     HumanInTheLoopMiddleware, BudgetWarningMiddleware):
        assert expected in kinds, f"missing {expected.__name__}"


def test_call_log_counts_model_calls(fake_model):
    log = CallLogMiddleware()
    model = fake_model(tool_call("spending_summary"), AIMessage("done"))
    build_agent(model, middleware=[log]).invoke({"messages": [{"role": "user", "content": "summary?"}]})
    assert log.calls == [1, 3]  # 1st call: the question; 2nd: question + tool call + tool result


def _delete_agent(fake_model, expense_id):
    model = fake_model(tool_call("delete_expense", expense_id=expense_id), AIMessage("finished"))
    return build_agent(model, checkpointer=InMemorySaver(), middleware=build_middleware())


def test_delete_needs_approval_and_reject_keeps_row(fake_model):
    expense_id = db.insert_expense(Expense(amount=100, category="food", description="pizza"))
    agent = _delete_agent(fake_model, expense_id)

    result = agent.invoke({"messages": [{"role": "user", "content": f"delete {expense_id}"}]}, CONFIG)
    assert "__interrupt__" in result, "delete_expense must pause for approval"

    agent.invoke(Command(resume={"decisions": [{"type": "reject", "message": "no"}]}), CONFIG)
    assert db.spending_by_category() == {"food": 100}


def test_delete_runs_after_approval(fake_model):
    expense_id = db.insert_expense(Expense(amount=100, category="food", description="pizza"))
    agent = _delete_agent(fake_model, expense_id)
    agent.invoke({"messages": [{"role": "user", "content": f"delete {expense_id}"}]}, CONFIG)
    agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), CONFIG)
    assert db.spending_by_category() == {}


def test_credit_card_is_masked_before_the_model_sees_it(fake_model):
    agent = build_agent(fake_model(AIMessage("ok")), middleware=build_middleware())
    result = agent.invoke({"messages": [{"role": "user", "content": "paid with 4111111111111111"}]})
    assert "4111111111111111" not in result["messages"][0].content


def test_budget_warning(fake_model):
    db.insert_expense(Expense(amount=500, category="shopping", description="shoes", spent_on=date.today()))
    over = build_agent(fake_model(AIMessage("ok")), middleware=[BudgetWarningMiddleware(monthly_budget=100)])
    under = build_agent(fake_model(AIMessage("ok")), middleware=[BudgetWarningMiddleware(monthly_budget=1000)])

    assert "Budget alert" in over.invoke({"messages": [{"role": "user", "content": "hi"}]})["messages"][-1].content
    assert under.invoke({"messages": [{"role": "user", "content": "hi"}]})["messages"][-1].content == "ok"
