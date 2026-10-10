"""Real-LLM checks (cost a few cents). Run: RUN_LLM_TESTS=1 pytest -m llm"""

import os
from datetime import date, timedelta

import pytest
from dotenv import load_dotenv

pytestmark = [
    pytest.mark.llm,
    pytest.mark.skipif(os.getenv("RUN_LLM_TESTS") != "1", reason="set RUN_LLM_TESTS=1 to call a real model"),
]


@pytest.fixture(scope="module")
def model():
    load_dotenv()
    from expense_assistant.models import get_model

    return get_model()


def test_parser_understands_relative_dates(model):
    from expense_assistant.prompts import build_expense_parser

    expense = build_expense_parser(model).invoke({"text": "I spent 250 rupees on pizza yesterday"})
    assert expense.amount == 250
    assert expense.category == "food"
    assert expense.spent_on == date.today() - timedelta(days=1)


@pytest.mark.parametrize("text, intent", [
    ("Paid 60 for an auto rickshaw", "log_expense"),
    ("How much did I spend on food this month?", "question"),
    ("Hey, how are you?", "chat"),
])
def test_intent_classifier(model, text, intent):
    from expense_assistant.prompts import build_intent_classifier

    assert build_intent_classifier(model).invoke({"text": text}).intent == intent
