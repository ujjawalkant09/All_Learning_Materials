"""Milestone 3 · prompts.py — run: pytest tests/test_m3_prompts.py"""

from datetime import date

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import Runnable

from expense_assistant.models import get_model
from expense_assistant.prompts import (
    build_expense_parser,
    build_intent_classifier,
    build_summary_chain,
    expense_parser_prompt,
    intent_prompt,
)


def test_parser_prompt_only_needs_text():
    prompt = expense_parser_prompt()
    assert prompt.input_variables == ["text"], "fill today/categories with .partial(...)"


def test_parser_prompt_mentions_today_and_categories():
    text = expense_parser_prompt().invoke({"text": "spent 100 on tea"}).to_string()
    assert date.today().isoformat() in text
    assert "food" in text and "transport" in text
    assert "spent 100 on tea" in text


def test_intent_prompt_history_is_optional():
    without = intent_prompt().invoke({"text": "hi"}).to_messages()
    with_history = intent_prompt().invoke(
        {"text": "and today?", "history": [HumanMessage("what did I spend?"), AIMessage("500")]}
    ).to_messages()
    assert len(with_history) == len(without) + 2


def test_summary_chain_returns_plain_string():
    chain = build_summary_chain(FakeListChatModel(responses=["You spent most on food."]))
    assert chain.invoke({"totals": {"food": 500}}) == "You spent most on food."


def test_structured_chains_can_be_built():
    model = get_model()
    assert isinstance(build_expense_parser(model), Runnable)
    assert isinstance(build_intent_classifier(model), Runnable)
