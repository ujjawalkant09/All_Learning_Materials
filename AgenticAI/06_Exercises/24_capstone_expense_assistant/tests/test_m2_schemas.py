"""Milestone 2 · schemas.py — run: pytest tests/test_m2_schemas.py"""

from datetime import date

import pytest
from pydantic import ValidationError

from expense_assistant.schemas import CATEGORIES, Expense, Intent


def test_categories():
    assert set(CATEGORIES) == {"food", "transport", "shopping", "bills", "entertainment", "health", "other"}


def test_valid_expense_defaults_to_today():
    expense = Expense(amount=250, category="food", description="pizza")
    assert expense.spent_on == date.today()


def test_date_string_is_parsed():
    assert Expense(amount=1, category="food", description="tea", spent_on="2026-01-31").spent_on == date(2026, 1, 31)


@pytest.mark.parametrize("bad", [
    {"amount": -5, "category": "food", "description": "pizza"},
    {"amount": 0, "category": "food", "description": "pizza"},
    {"amount": 10, "category": "crypto", "description": "coins"},
    {"amount": 10, "category": "food", "description": "x"},
])
def test_invalid_expenses_are_rejected(bad):
    with pytest.raises(ValidationError):
        Expense(**bad)


def test_fields_have_descriptions_for_the_llm():
    assert set(Expense.model_fields) == {"amount", "category", "description", "spent_on"}
    for name, field in Expense.model_fields.items():
        assert field.description, f"Expense.{name} needs a Field(description=...)"


def test_intent_only_allows_three_values():
    assert Intent(intent="question", reason="asks about spending").intent == "question"
    with pytest.raises(ValidationError):
        Intent(intent="dance", reason="?")
