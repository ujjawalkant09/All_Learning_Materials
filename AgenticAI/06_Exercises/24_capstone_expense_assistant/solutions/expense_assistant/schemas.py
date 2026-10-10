"""Milestone 2 · Schemas  (revise: steps 03, 07)

Pydantic models give us validated data. Field descriptions are also sent to the LLM
when a model is used with ``with_structured_output``.
"""

from datetime import date
from typing import Literal, get_args

from pydantic import BaseModel, Field

Category = Literal["food", "transport", "shopping", "bills", "entertainment", "health", "other"]
CATEGORIES: tuple[str, ...] = get_args(Category)


class Expense(BaseModel):
    """A single expense the user made."""

    amount: float = Field(gt=0, description="Amount spent, a positive number")
    category: Category = Field(description="The best matching category")
    description: str = Field(min_length=2, max_length=100, description="Short description, e.g. 'pizza with friends'")
    spent_on: date = Field(
        default_factory=date.today,
        description="Date of the expense as YYYY-MM-DD; today if the user does not mention one",
    )


class Intent(BaseModel):
    """What the user wants, used by the LangGraph router."""

    intent: Literal["log_expense", "question", "chat"] = Field(
        description="log_expense = user reports money spent; question = asks about their spending; chat = anything else"
    )
    reason: str = Field(description="One short sentence explaining the choice")
