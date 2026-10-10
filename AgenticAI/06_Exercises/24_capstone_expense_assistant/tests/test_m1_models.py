"""Milestone 1 · models.py — run: pytest tests/test_m1_models.py"""

from expense_assistant.models import DEFAULT_MODEL, get_model


def test_default_model_is_used():
    model = get_model()
    assert DEFAULT_MODEL.endswith(model.model_name)


def test_temperature_is_passed_through():
    assert get_model(temperature=0.7).temperature == 0.7


def test_env_var_overrides_default(monkeypatch):
    monkeypatch.setenv("EXPENSE_MODEL", "openai:gpt-4o")
    assert get_model().model_name == "gpt-4o"


def test_argument_beats_env_var(monkeypatch):
    monkeypatch.setenv("EXPENSE_MODEL", "openai:gpt-4o")
    assert get_model("openai:gpt-4.1").model_name == "gpt-4.1"
