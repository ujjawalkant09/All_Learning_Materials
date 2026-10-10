"""Milestone 4a · Database  (revise: step 21 SQL project)

Plain ``sqlite3``, with no LLM involved. Connection handling and ``seed_sample_data`` are given;
you write the queries.

Table::

    expenses(id INTEGER PRIMARY KEY, amount REAL, category TEXT, description TEXT, spent_on TEXT 'YYYY-MM-DD')

Check: pytest tests/test_m4_db_and_tools.py
"""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

from .schemas import Expense

DEFAULT_DB = Path(__file__).resolve().parent.parent / "expenses.db"


def get_db_path() -> Path:
    """Database file: ``EXPENSE_DB`` env var if set (tests use this), else ``expenses.db`` next to the package."""
    return Path(os.getenv("EXPENSE_DB", DEFAULT_DB))


@contextmanager
def connect(readonly: bool = False) -> Iterator[sqlite3.Connection]:
    """Open a connection, commit on success and always close it. (Given.)

    ``readonly=True`` opens the file with ``mode=ro`` so even a malicious query cannot write.
    Usage::

        with connect() as conn:
            conn.execute("...", (param1, param2))
    """
    path = get_db_path()
    conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) if readonly else sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the ``expenses`` table if it does not exist.

    TODO (M4): ``CREATE TABLE IF NOT EXISTS expenses (...)`` with the columns in the module docstring
      (id INTEGER PRIMARY KEY AUTOINCREMENT, the rest NOT NULL).
    """
    raise NotImplementedError("M4: implement init_db")


def insert_expense(expense: Expense) -> int:
    """Save a validated expense and return its new id.

    TODO (M4): INSERT with ``?`` placeholders (never f-strings!). Store the date as ``expense.spent_on.isoformat()``.
      Return ``cursor.lastrowid``.
    """
    raise NotImplementedError("M4: implement insert_expense")


def delete_expense(expense_id: int) -> bool:
    """Delete an expense. Returns ``True`` if a row was deleted.  TODO (M4): hint: ``cursor.rowcount``"""
    raise NotImplementedError("M4: implement delete_expense")


def run_readonly_query(sql: str) -> list[tuple]:
    """Run a SELECT written by the LLM on a read-only connection.

    TODO (M4):
      - raise ``ValueError`` unless the SQL starts with "select" or "with" (ignore case and leading spaces)
      - run it with ``connect(readonly=True)`` and return ``fetchall()``
    """
    raise NotImplementedError("M4: implement run_readonly_query")


def spending_by_category(start: date | None = None, end: date | None = None) -> dict[str, float]:
    """Total amount per category between ``start`` and ``end`` (inclusive, both optional).

    Example: ``{"food": 150.0, "transport": 30.0}``, sorted by total, highest first.

    TODO (M4): build the WHERE clause only for the dates that were given; ``GROUP BY category``;
      return ``dict(rows)``.
    """
    raise NotImplementedError("M4: implement spending_by_category")


def seed_sample_data() -> None:
    """Insert a few example expenses if the table is empty. (Given; used by ``cli --seed``.)"""
    init_db()
    with connect() as conn:
        if conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]:
            return
    today = date.today()
    for amount, category, description, days_ago in [
        (250, "food", "pizza with friends", 1),
        (60, "transport", "metro card recharge", 2),
        (1499, "shopping", "running shoes", 5),
        (899, "bills", "mobile recharge", 10),
        (450, "entertainment", "movie tickets", 12),
    ]:
        insert_expense(Expense(amount=amount, category=category, description=description,
                               spent_on=today - timedelta(days=days_ago)))
