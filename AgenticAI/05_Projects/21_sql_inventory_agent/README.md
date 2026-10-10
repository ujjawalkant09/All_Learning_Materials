# 21 · Project — Natural-Language → SQL Inventory Agent

Ask questions in plain English ("total stock value per warehouse"). The agent writes the SQL, runs it on
SQLite through a tool and returns structured rows.

| File | Purpose |
|---|---|
| `sql_agent.ipynb` | the agent: walk through it top to bottom |
| `inventory.db` | SQLite database with an `inventory` table (1000 demo rows) |
| `seed_inventory_db.py` | regenerate the data: `python seed_inventory_db.py --reset` |

**Concepts used:** `@tool` [09] · `create_agent` + `system_prompt` [10] · `response_format` [12]

**Why it's built this way:** the model has to *write* queries and may retry after an error, so it is an agent.
The flow is the standard tool loop, so `create_agent` is enough and LangGraph isn't needed. The DB is opened
read-only because the SQL comes from the LLM. See [20 · When to use what](../../04_When_To_Use_What/20_choosing_the_right_tool.md).
