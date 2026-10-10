"""Milestone 4b · Tools  (revise: step 09)

Each tool is a thin wrapper around ``db``. The docstring is what the LLM reads, so it explains
arguments and formats. Tools return **strings**, and errors are returned as text (not raised)
so the agent can read them and try again.
"""

import json
from datetime import date

from langchain.tools import tool
from pydantic import ValidationError

from . import db
from .schemas import Expense


@tool
def add_expense(amount: float, category: str, description: str, spent_on: str | None = None) -> str:
    """Save a new expense.

    amount: positive amount spent.
    category: one of food, transport, shopping, bills, entertainment, health, other.
    description: short description of what was bought.
    spent_on: date as YYYY-MM-DD; leave empty for today.
    """
    data = {"amount": amount, "category": category, "description": description}
    if spent_on:
        data["spent_on"] = spent_on
    try:
        expense = Expense(**data)
    except ValidationError as error:
        problems = "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in error.errors())
        return f"Could not save expense: {problems}"
    expense_id = db.insert_expense(expense)
    return (f"Saved expense #{expense_id}: {expense.amount:.2f} for {expense.description} "
            f"({expense.category}) on {expense.spent_on}")


@tool
def delete_expense(expense_id: int) -> str:
    """Permanently delete an expense by its id."""
    if db.delete_expense(expense_id):
        return f"Deleted expense #{expense_id}"
    return f"No expense with id {expense_id}"


@tool
def query_expenses(sql: str) -> str:
    """Run a read-only SQLite SELECT query and return the rows.

    Table: expenses(id INTEGER, amount REAL, category TEXT, description TEXT, spent_on TEXT as 'YYYY-MM-DD').
    """
    try:
        rows = db.run_readonly_query(sql)
    except Exception as error:
        return f"Query failed, fix the SQL and try again: {error}"
    return str(rows) if rows else "No rows."


@tool
def spending_summary(start_date: str | None = None, end_date: str | None = None) -> str:
    """Total spent per category, optionally between start_date and end_date (YYYY-MM-DD, inclusive)."""
    totals = db.spending_by_category(
        date.fromisoformat(start_date) if start_date else None,
        date.fromisoformat(end_date) if end_date else None,
    )
    return json.dumps(totals) if totals else "No expenses in that period."


ALL_TOOLS = [add_expense, delete_expense, query_expenses, spending_summary]
READ_ONLY_TOOLS = [query_expenses, spending_summary]
