"""Milestone 6 · Middleware  (revise: steps 13, 14, 15)

Goal: built-in middleware (summarisation, PII, approvals) plus two of your own.
Check: pytest tests/test_m6_middleware.py
"""

from datetime import date  # noqa: F401

from langchain.agents.middleware import (  # noqa: F401
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    SummarizationMiddleware,
)
from langchain.messages import AIMessage  # noqa: F401

from . import db  # noqa: F401


class CallLogMiddleware(AgentMiddleware):
    """Remember how many messages were sent on every model call.

    TODO (M6):
      - in ``__init__``: call ``super().__init__()`` and create ``self.calls = []``
      - add a ``before_model(self, state, runtime)`` hook that appends ``len(state["messages"])``
        and returns ``None``
    """


class BudgetWarningMiddleware(AgentMiddleware):
    """After the agent finishes, add a warning if this month's spending is over budget.

    TODO (M6):
      - ``__init__(self, monthly_budget)``: store it (and call ``super().__init__()``)
      - ``after_agent(self, state, runtime)``: sum ``db.spending_by_category(start=<1st of this month>)``;
        if it is over budget return ``{"messages": [AIMessage("⚠️ Budget alert: ...")]}``, else ``None``.
        hint: ``date.today().replace(day=1)``
    """


def build_middleware(monthly_budget: float = 20_000, summary_model: str = "openai:gpt-4o-mini") -> list[AgentMiddleware]:
    """All middleware for the CLI agent, in order.

    TODO (M6): return a list with:
      - CallLogMiddleware()
      - SummarizationMiddleware(model=summary_model, trigger=("messages", 30), keep=("messages", 10))
      - PIIMiddleware for "credit_card" (strategy "mask") and "email" (strategy "redact"), on input
      - HumanInTheLoopMiddleware that interrupts on "delete_expense" (allowed: approve, reject)
      - BudgetWarningMiddleware(monthly_budget)
    """
    raise NotImplementedError("M6: implement build_middleware")
