"""Milestone 3 · Prompts & chains  (revise: steps 05, 06, 07)

Goal: three LCEL chains, each ``prompt | model | output``:
- expense parser:    text -> ``Expense``   (structured output)
- intent classifier: text -> ``Intent``    (structured output)
- summary chain:     totals -> ``str``     (``StrOutputParser``)

Check: pytest tests/test_m3_prompts.py
"""

from datetime import date  # noqa: F401

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser  # noqa: F401
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # noqa: F401
from langchain_core.runnables import Runnable

from .schemas import CATEGORIES, Expense, Intent  # noqa: F401


def expense_parser_prompt() -> ChatPromptTemplate:
    """Prompt that turns free text into an expense.

    TODO (M3):
      - ``ChatPromptTemplate.from_messages`` with a system message that mentions ``{today}`` and
        ``{categories}`` and asks to resolve words like "yesterday" to YYYY-MM-DD, then ``("human", "{text}")``
      - call ``.partial(today=..., categories=...)`` so the only remaining input is ``text``.
        Pass ``today`` as a *function* (``lambda: date.today().isoformat()``) so it's fresh on each run.
    """
    raise NotImplementedError("M3: implement expense_parser_prompt")


def intent_prompt() -> ChatPromptTemplate:
    """Prompt that classifies the user's latest message.

    TODO (M3): system message explaining the three intents, then
      ``MessagesPlaceholder("history", optional=True)``, then ``("human", "{text}")``.
    """
    raise NotImplementedError("M3: implement intent_prompt")


def summary_prompt() -> ChatPromptTemplate:
    """Prompt that turns category totals into a short report.

    TODO (M3): system = friendly finance coach; human message uses ``{totals}`` and asks for a
      3-sentence summary with one saving tip.
    """
    raise NotImplementedError("M3: implement summary_prompt")


def build_expense_parser(model: BaseChatModel) -> Runnable:
    """``{"text": ...}`` -> ``Expense``.  TODO (M3): prompt | model.with_structured_output(Expense)"""
    raise NotImplementedError("M3: implement build_expense_parser")


def build_intent_classifier(model: BaseChatModel) -> Runnable:
    """``{"text": ...}`` -> ``Intent``.  TODO (M3)"""
    raise NotImplementedError("M3: implement build_intent_classifier")


def build_summary_chain(model: BaseChatModel) -> Runnable:
    """``{"totals": ...}`` -> ``str``.  TODO (M3): prompt | model | StrOutputParser()"""
    raise NotImplementedError("M3: implement build_summary_chain")
