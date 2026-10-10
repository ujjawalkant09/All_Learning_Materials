"""Milestone 3 · Prompts & chains  (revise: steps 05, 06, 07)

Three LCEL chains, each ``prompt | model | output``:
- expense parser:    text -> ``Expense``   (structured output)
- intent classifier: text -> ``Intent``    (structured output, used by the graph router)
- summary chain:     totals -> ``str``     (plain text via ``StrOutputParser``)
"""

from datetime import date

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable

from .schemas import CATEGORIES, Expense, Intent


def expense_parser_prompt() -> ChatPromptTemplate:
    """Prompt that turns free text into an expense.

    ``today`` and ``categories`` are filled in with ``.partial`` so the only input left is ``{text}``.
    ``today`` is a function, so it is evaluated each time the prompt runs (not once at import).
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You extract a single expense from the user's message. Today is {today}. "
            "Resolve relative dates like 'yesterday' to YYYY-MM-DD. "
            "Allowed categories: {categories}.",
        ),
        ("human", "{text}"),
    ]).partial(today=lambda: date.today().isoformat(), categories=", ".join(CATEGORIES))


def intent_prompt() -> ChatPromptTemplate:
    """Prompt that classifies a message; earlier turns can be passed as optional ``history``."""
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "Classify the user's latest message for an expense-tracker assistant.\n"
            "- log_expense: the user tells you about money they spent\n"
            "- question: the user asks about their past expenses or spending\n"
            "- chat: anything else (greetings, general questions)",
        ),
        MessagesPlaceholder("history", optional=True),
        ("human", "{text}"),
    ])


def summary_prompt() -> ChatPromptTemplate:
    """Prompt that turns category totals into a short, friendly report."""
    return ChatPromptTemplate.from_messages([
        ("system", "You are a friendly personal-finance coach. Be concise."),
        ("human", "My spending per category: {totals}\nWrite a 3-sentence summary with one saving tip."),
    ])


def build_expense_parser(model: BaseChatModel) -> Runnable:
    """``{"text": ...}`` -> ``Expense``."""
    return expense_parser_prompt() | model.with_structured_output(Expense)


def build_intent_classifier(model: BaseChatModel) -> Runnable:
    """``{"text": ..., "history": [...]?}`` -> ``Intent``."""
    return intent_prompt() | model.with_structured_output(Intent)


def build_summary_chain(model: BaseChatModel) -> Runnable:
    """``{"totals": ...}`` -> ``str``."""
    return summary_prompt() | model | StrOutputParser()
