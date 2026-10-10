**Part 6 · Exercises** · step 25 of 25
[← 23 Concept drills](../23_concept_drills.ipynb) · [🏠 Roadmap](../../README.md) · 🎉 final step

# 24 · Capstone — Build an AI Expense Assistant

Build a real Python project (not a notebook) that uses **every concept from the course**: a chat assistant
that records your expenses, answers questions about your spending, asks before deleting anything,
masks card numbers and warns you when you're over budget.

```
You: I spent 250 on pizza yesterday
Assistant: Saved expense #6: 250.00 for pizza (food) on 2026-10-09
You: how much did I spend on food this month?
Assistant: You spent ₹250 on food this month.
You: delete expense 6
Approve delete_expense({'expense_id': 6})? [y/n] n
Assistant: Okay, I won't delete it.
```

---

## How it works

You write the code in `expense_assistant/`. Every file has a docstring explaining the goal, `TODO` hints
and links to the step that teaches the concept. Each milestone has its own **tests**, so you know when you're done.

```
24_capstone_expense_assistant/
├── expense_assistant/     ← ✍️ YOUR CODE (starter with TODOs)
│   ├── models.py          M1
│   ├── schemas.py         M2
│   ├── prompts.py         M3
│   ├── db.py, tools.py    M4
│   ├── agent.py           M5
│   ├── middleware.py      M6
│   ├── graph.py           M7
│   └── cli.py             M8
├── tests/                 ← one test file per milestone (all offline and free, thanks to fake models)
└── solutions/             ← reference implementation. Peek only when stuck!
```

### Commands (run inside this folder)

```bash
source ../../.venv/bin/activate              # the shared AgenticAI environment

pytest tests/test_m1_models.py               # check one milestone
pytest                                       # check everything
USE_SOLUTIONS=1 pytest                       # run the same tests against the reference solution
RUN_LLM_TESTS=1 pytest -m llm                # optional: real-LLM checks (needs OPENAI_API_KEY, costs cents)

python -m expense_assistant.cli --seed               # chat! (agent mode, needs OPENAI_API_KEY)
python -m expense_assistant.cli --mode graph         # chat using the LangGraph router
```

At the start, all 46 tests fail with messages like `NotImplementedError: M1: implement get_model`.
Your goal is to get to **46 passed**.

---

## Milestones

Do them in order; each builds on the previous one.

| # | File | You build | Concepts revised | Steps |
|---|---|---|---|---|
| M1 | `models.py` | `get_model()`: argument → env var → default | `init_chat_model`, providers, temperature | 01, 04 |
| M2 | `schemas.py` | `Expense`, `Intent` with validation | Pydantic, `Field`, `Literal` | 03, 07 |
| M3 | `prompts.py` | parser, classifier and summary chains | `ChatPromptTemplate`, `.partial`, `MessagesPlaceholder`, LCEL, `with_structured_output`, `StrOutputParser` | 05, 06, 07 |
| M4 | `db.py`, `tools.py` | SQLite access + 4 tools | `@tool`, docstrings as instructions, errors as text, read-only SQL | 09, 21 |
| M5 | `agent.py` | `build_agent()`, `ask()` | `create_agent`, system prompt, checkpointer, `thread_id` | 10, 11 |
| M6 | `middleware.py` | 2 custom + 4 built-in middleware | `before_model`, `after_agent`, summarization, PII, human-in-the-loop | 13, 14, 15 |
| M7 | `graph.py` | intent router graph | `StateGraph`, reducers, conditional edges, dependency injection | 16, 17, 18 |
| M8 | `cli.py` | approval prompts + reply printing | interrupts, `Command(resume=...)`, chat loop | 08, 14 |

### Design decisions to notice (step 20 in action)
- **Logging an expense doesn't use an agent.** The graph classifies the message, then a structured-output chain
  parses it. That's one cheap, predictable call, not a tool loop.
- **Questions go to a read-only agent** (`READ_ONLY_TOOLS`). In graph mode it physically can't delete data.
  This is called *least privilege*.
- **The agent mode** has every tool, so `delete_expense` is protected by human-in-the-loop instead.
- **The LLM writes SQL**, so the DB connection is opened read-only (`mode=ro`) for those queries.
- **Dependencies are injected** into `build_graph(...)` (classifier, parser, agent, model), which is why the
  graph can be tested with fakes and no API calls.

---

## Bonus challenges (no tests, so you decide when they're done)
1. **Streaming:** print the assistant's answer token by token (`app.stream(..., stream_mode="messages")`). *(step 04)*
2. **Monthly report:** add a `report` command that runs `build_summary_chain` on `spending_by_category()`. *(step 06)*
3. **Batch import:** categorise a list of bank-statement lines with `parser.batch([...])`. *(step 04)*
4. **Persistent memory:** replace `InMemorySaver` with a SQLite checkpointer so chats survive restarts.
   Hint: `uv add langgraph-checkpoint-sqlite`. *(step 11)*
5. **Switch provider:** `EXPENSE_MODEL="groq:qwen/qwen3-32b" python -m expense_assistant.cli`. Does it still pass `pytest -m llm`? *(step 04)*
6. **Web tool:** add a currency-conversion or price-lookup tool using Tavily. *(step 19)*
7. **Tracing:** set `LANGSMITH_TRACING=true` and look at one full conversation in LangSmith. *(step 02)*

## Self-check: can you explain…
- why tools return error **text** instead of raising?
- why `build_agent(tools=[])` must not fall back to `ALL_TOOLS`?
- why `intent` has no reducer but `saved_ids` uses `operator.add`?
- why the parser prompt uses `.partial(today=lambda: ...)` instead of a fixed string?
- why the fake model needs a *different* `AIMessage` object for every turn? (Hint: message ids and `add_messages`.)

---
🎉 **Course complete.** [🏠 Back to the roadmap](../../README.md)
