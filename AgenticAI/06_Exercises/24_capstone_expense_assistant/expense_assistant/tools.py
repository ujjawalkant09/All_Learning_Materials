"""Milestone 4b · Tools  (revise: step 09)

Each tool is a thin wrapper around ``db``. Rules for good tools:
- the docstring is what the LLM reads, so explain arguments and formats;
- return **strings**;
- return errors as text instead of raising, so the agent can read them and retry.

Check: pytest tests/test_m4_db_and_tools.py
"""

import json  # noqa: F401
from datetime import date  # noqa: F401

from langchain.tools import tool
from pydantic import ValidationError  # noqa: F401

from . import db  # noqa: F401
from .schemas import Expense  # noqa: F401


@tool
def add_expense(amount: float, category: str, description: str, spent_on: str | None = None) -> str:
    """Save a new expense.

    amount: positive amount spent.
    category: one of food, transport, shopping, bills, entertainment, health, other.
    description: short description of what was bought.
    spent_on: date as YYYY-MM-DD; leave empty for today.
    """
    # TODO (M4): build an Expense (only pass spent_on if given) inside try/except ValidationError.
    #   On error return a message starting with "Could not save expense".
    #   On success save with db.insert_expense and return a message starting with "Saved expense #<id>".
    raise NotImplementedError("M4: implement add_expense")


@tool
def delete_expense(expense_id: int) -> str:
    """Permanently delete an expense by its id."""
    # TODO (M4): return "Deleted expense #<id>" or "No expense with id <id>"
    raise NotImplementedError("M4: implement delete_expense")


@tool
def query_expenses(sql: str) -> str:
    """Run a read-only SQLite SELECT query and return the rows.

    Table: expenses(id INTEGER, amount REAL, category TEXT, description TEXT, spent_on TEXT as 'YYYY-MM-DD').
    """
    # TODO (M4): call db.run_readonly_query; on ANY exception return "Query failed, fix the SQL and try again: <error>"
    #   return str(rows), or "No rows." if empty
    raise NotImplementedError("M4: implement query_expenses")


@tool
def spending_summary(start_date: str | None = None, end_date: str | None = None) -> str:
    """Total spent per category, optionally between start_date and end_date (YYYY-MM-DD, inclusive)."""
    # TODO (M4): convert the strings with date.fromisoformat (if given), call db.spending_by_category,
    #   return json.dumps(totals) or "No expenses in that period."
    raise NotImplementedError("M4: implement spending_summary")


ALL_TOOLS = [add_expense, delete_expense, query_expenses, spending_summary]
# TODO (M4): the tools that can't change data (used by the graph's question-answering agent)
READ_ONLY_TOOLS = []
