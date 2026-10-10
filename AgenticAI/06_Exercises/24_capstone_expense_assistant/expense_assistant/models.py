"""Milestone 1 · Chat models  (revise: steps 01, 04)

Goal: one function that decides which LLM the whole app uses.
Check: pytest tests/test_m1_models.py
"""

import os  # noqa: F401  (you will need it)

from langchain_core.language_models import BaseChatModel

DEFAULT_MODEL = "openai:gpt-4o-mini"


def get_model(model_name: str | None = None, temperature: float = 0.0) -> BaseChatModel:
    """Create the chat model used by the app.

    The model name is chosen in this order:
    1. the ``model_name`` argument,
    2. the ``EXPENSE_MODEL`` environment variable (e.g. ``"groq:qwen/qwen3-32b"``),
    3. ``DEFAULT_MODEL``.

    TODO (M1):
      - pick the name using the order above (hint: ``a or b or c``)
      - return ``init_chat_model(name, temperature=temperature)``  (from ``langchain.chat_models``)
    """
    raise NotImplementedError("M1: implement get_model")
