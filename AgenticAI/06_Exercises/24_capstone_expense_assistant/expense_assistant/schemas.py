"""Milestone 2 · Schemas  (revise: steps 03, 07)

Goal: Pydantic models for validated data. Field descriptions are sent to the LLM in structured output.
Check: pytest tests/test_m2_schemas.py
"""

from datetime import date  # noqa: F401
from typing import Literal, get_args

from pydantic import BaseModel, Field  # noqa: F401

# TODO (M2): list all 7 categories: food, transport, shopping, bills, entertainment, health, other
Category = Literal["other"]
CATEGORIES: tuple[str, ...] = get_args(Category)


class Expense(BaseModel):
    """A single expense the user made.

    TODO (M2): add four fields, each with ``Field(..., description="...")``:
      - amount: float, must be > 0                          (hint: ``gt=0``)
      - category: Category
      - description: str, 2 to 100 characters              (hint: ``min_length``, ``max_length``)
      - spent_on: date, defaults to today                   (hint: ``default_factory=date.today``)
    """


class Intent(BaseModel):
    """What the user wants, used by the LangGraph router (Milestone 7).

    TODO (M2): add two fields with descriptions:
      - intent: exactly one of "log_expense", "question", "chat"   (hint: ``Literal[...]``)
      - reason: str — one short sentence explaining the choice
    """
