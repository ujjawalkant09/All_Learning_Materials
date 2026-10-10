"""Milestone 4 · db.py + tools.py — run: pytest tests/test_m4_db_and_tools.py"""

import json
from datetime import date

import pytest

from expense_assistant import db
from expense_assistant.schemas import Expense
from expense_assistant.tools import (
    ALL_TOOLS,
    READ_ONLY_TOOLS,
    add_expense,
    delete_expense,
    query_expenses,
    spending_summary,
)


def save(amount, category="food", description="pizza", spent_on=None):
    return db.insert_expense(Expense(amount=amount, category=category, description=description,
                                     spent_on=spent_on or date.today()))


# ---------- db.py
def test_insert_returns_increasing_ids():
    assert save(100) < save(200)


def test_spending_by_category_and_date_filter():
    save(100, "food", spent_on=date(2026, 1, 1))
    save(50, "food", spent_on=date(2026, 2, 1))
    save(30, "transport", spent_on=date(2026, 2, 2))
    assert db.spending_by_category() == {"food": 150, "transport": 30}
    assert db.spending_by_category(start=date(2026, 2, 1)) == {"food": 50, "transport": 30}


def test_delete_expense():
    expense_id = save(100)
    assert db.delete_expense(expense_id) is True
    assert db.delete_expense(expense_id) is False


def test_readonly_query_rejects_writes():
    save(100)
    assert db.run_readonly_query("SELECT amount FROM expenses") == [(100.0,)]
    with pytest.raises(ValueError):
        db.run_readonly_query("DELETE FROM expenses")


# ---------- tools.py
def test_tool_names_and_lists():
    assert {t.name for t in ALL_TOOLS} == {"add_expense", "delete_expense", "query_expenses", "spending_summary"}
    assert {t.name for t in READ_ONLY_TOOLS} == {"query_expenses", "spending_summary"}
    assert all(t.description for t in ALL_TOOLS), "every tool needs a docstring"


def test_add_expense_tool_saves_row():
    reply = add_expense.invoke({"amount": 250, "category": "food", "description": "pizza", "spent_on": "2026-03-01"})
    assert "Saved" in reply
    assert db.run_readonly_query("SELECT amount, spent_on FROM expenses") == [(250.0, "2026-03-01")]


def test_add_expense_tool_returns_error_text_instead_of_raising():
    reply = add_expense.invoke({"amount": 10, "category": "crypto", "description": "coins"})
    assert "Could not save" in reply
    assert db.run_readonly_query("SELECT COUNT(*) FROM expenses") == [(0,)]


def test_query_tool_handles_bad_sql():
    assert "Query failed" in query_expenses.invoke({"sql": "SELEC nonsense"})
    assert "Query failed" in query_expenses.invoke({"sql": "DROP TABLE expenses"})


def test_query_tool_returns_rows():
    save(100)
    assert "100.0" in query_expenses.invoke({"sql": "SELECT amount FROM expenses"})


def test_delete_and_summary_tools():
    expense_id = save(100)
    save(40, "transport")
    assert json.loads(spending_summary.invoke({})) == {"food": 100, "transport": 40}
    assert "Deleted" in delete_expense.invoke({"expense_id": expense_id})
    assert "No expense" in delete_expense.invoke({"expense_id": expense_id})
