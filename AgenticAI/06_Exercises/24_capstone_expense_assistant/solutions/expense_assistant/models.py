"""Milestone 1 · Chat models  (revise: steps 01, 04)

One place that decides which LLM the whole app uses, so switching provider is a one-line change.
"""

import os

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

DEFAULT_MODEL = "openai:gpt-4o-mini"


def get_model(model_name: str | None = None, temperature: float = 0.0) -> BaseChatModel:
    """Create the chat model used by the app.

    The model name is chosen in this order:
    1. the ``model_name`` argument,
    2. the ``EXPENSE_MODEL`` environment variable (e.g. ``"groq:qwen/qwen3-32b"``),
    3. ``DEFAULT_MODEL``.

    Args:
        model_name: A ``"provider:model"`` string understood by ``init_chat_model``.
        temperature: 0 keeps answers deterministic, which suits extraction and SQL.
    """
    name = model_name or os.getenv("EXPENSE_MODEL") or DEFAULT_MODEL
    return init_chat_model(name, temperature=temperature)
