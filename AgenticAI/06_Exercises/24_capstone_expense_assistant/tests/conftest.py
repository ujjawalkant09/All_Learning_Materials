"""Shared test setup.

- ``USE_SOLUTIONS=1 pytest`` runs the tests against ``solutions/`` instead of your code.
- Every test gets its own empty SQLite file (``EXPENSE_DB``), so tests never touch ``expenses.db``.
- ``FakeToolModel`` replays scripted AIMessages, so agents and graphs run offline for free.
"""

import os
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "solutions" if os.getenv("USE_SOLUTIONS") == "1" else PROJECT))

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402


class FakeToolModel(FakeMessagesListChatModel):
    """A fake chat model that returns ``responses`` in order and accepts ``bind_tools``."""

    def bind_tools(self, tools, **kwargs):
        return self


def tool_call(name: str, call_id: str = "call_1", **args) -> AIMessage:
    """An AIMessage asking to run one tool — what a real model returns when it wants a tool."""
    return AIMessage("", tool_calls=[{"name": name, "args": args, "id": call_id}])


@pytest.fixture
def fake_model():
    """``fake_model(msg1, msg2, ...)`` -> a model that answers with those messages in order."""
    return lambda *responses: FakeToolModel(responses=list(responses))


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Fresh database per test, dummy API keys and no real LLM calls by accident."""
    monkeypatch.setenv("EXPENSE_DB", str(tmp_path / "test.db"))
    monkeypatch.delenv("EXPENSE_MODEL", raising=False)
    if os.getenv("RUN_LLM_TESTS") != "1":
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy")
    try:
        from expense_assistant import db

        db.init_db()
    except NotImplementedError:
        pass  # Milestone 4 not done yet — tests that need the DB will say so
