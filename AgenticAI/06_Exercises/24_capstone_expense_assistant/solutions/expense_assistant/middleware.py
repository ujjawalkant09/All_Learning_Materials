"""Milestone 6 · Middleware  (revise: steps 13, 14, 15)

Built-in middleware for summarisation, PII and approvals, plus two custom ones.
"""

from datetime import date

from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
)
from langchain.messages import AIMessage

from . import db


class CallLogMiddleware(AgentMiddleware):
    """Remember how many messages were sent on every model call (a ``before_model`` hook)."""

    def __init__(self) -> None:
        super().__init__()
        self.calls: list[int] = []

    def before_model(self, state, runtime):
        self.calls.append(len(state["messages"]))
        return None  # observe only


class BudgetWarningMiddleware(AgentMiddleware):
    """After the agent finishes, add a warning if this month's spending is over budget (``after_agent``)."""

    def __init__(self, monthly_budget: float) -> None:
        super().__init__()
        self.monthly_budget = monthly_budget

    def after_agent(self, state, runtime):
        spent = sum(db.spending_by_category(start=date.today().replace(day=1)).values())
        if spent > self.monthly_budget:
            return {"messages": [AIMessage(
                f"⚠️ Budget alert: you have spent {spent:.2f} this month, "
                f"over your budget of {self.monthly_budget:.2f}."
            )]}
        return None


def build_middleware(monthly_budget: float = 20_000, summary_model: str = "openai:gpt-4o-mini") -> list[AgentMiddleware]:
    """All middleware for the CLI agent, in the order they run."""
    return [
        CallLogMiddleware(),
        SummarizationMiddleware(model=summary_model, trigger=("messages", 30), keep=("messages", 10)),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        HumanInTheLoopMiddleware(interrupt_on={"delete_expense": {"allowed_decisions": ["approve", "reject"]}}),
        BudgetWarningMiddleware(monthly_budget),
    ]
