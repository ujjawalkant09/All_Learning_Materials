"""Milestone 4a · Database  (revise: step 21 SQL project)

Plain ``sqlite3`` — no LLM here. Keeping data access separate from tools makes it easy to test.

Table::

    expenses(id INTEGER PRIMARY KEY, amount REAL, category TEXT, description TEXT, spent_on TEXT 'YYYY-MM-DD')
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
    """Open a connection, commit on success and always close it.

    ``readonly=True`` opens the file with ``mode=ro`` so even a malicious query cannot write.
    """
    path = get_db_path()
    conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) if readonly else sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the ``expenses`` table if it does not exist."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                spent_on TEXT NOT NULL
            )
            """
        )


def insert_expense(expense: Expense) -> int:
    """Save a validated expense and return its new id."""
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO expenses (amount, category, description, spent_on) VALUES (?, ?, ?, ?)",
            (expense.amount, expense.category, expense.description, expense.spent_on.isoformat()),
        )
        return cursor.lastrowid


def delete_expense(expense_id: int) -> bool:
    """Delete an expense. Returns ``True`` if a row was deleted."""
    with connect() as conn:
        return conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,)).rowcount > 0


def run_readonly_query(sql: str) -> list[tuple]:
    """Run a SELECT written by the LLM on a read-only connection.

    Raises:
        ValueError: if the statement is not a SELECT / WITH query.
    """
    if not sql.lstrip().lower().startswith(("select", "with")):
        raise ValueError("Only SELECT queries are allowed")
    with connect(readonly=True) as conn:
        return conn.execute(sql).fetchall()


def spending_by_category(start: date | None = None, end: date | None = None) -> dict[str, float]:
    """Total amount per category between ``start`` and ``end`` (inclusive, both optional)."""
    query = "SELECT category, ROUND(SUM(amount), 2) FROM expenses WHERE 1 = 1"
    params: list[str] = []
    if start:
        query += " AND spent_on >= ?"
        params.append(start.isoformat())
    if end:
        query += " AND spent_on <= ?"
        params.append(end.isoformat())
    query += " GROUP BY category ORDER BY 2 DESC"
    with connect() as conn:
        return dict(conn.execute(query, params).fetchall())


def seed_sample_data() -> None:
    """Insert a few example expenses if the table is empty (handy for trying the CLI)."""
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
