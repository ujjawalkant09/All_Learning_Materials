**Part 4 · When to Use What** · step 20 of 25
[← 19 Research chatbot](../03_LangGraph/19_research_chatbot_multiple_tools.ipynb) · [🏠 Roadmap](../README.md) · [21 Project: SQL agent →](../05_Projects/21_sql_inventory_agent/sql_agent.ipynb)

# 20 · Choosing the Right Tool — When to Use What, and Why

You now know every building block. This page is the **decision guide**. Read it before starting the projects,
and come back whenever you start something new.

---

## 1. The one-minute decision tree

```
Do you need an LLM at all?  (rules / regex / SQL can't solve it)
│
├─ One question → one answer, no tools?
│     └─► a model call: init_chat_model(...).invoke()                          [04, 05]
│         need typed data back? → .with_structured_output(Schema)              [07]
│
├─ Fixed steps you can write down in advance? (template → model → parse → save)
│     └─► an LCEL chain: prompt | model | parser                               [06]
│
├─ The model must fetch data or take actions, and decide which / how many times?
│     └─► an agent: create_agent(model, tools, ...)                            [10]
│         + memory           → checkpointer + thread_id                        [11]
│         + typed answer     → response_format=Schema                          [12]
│         + long chats       → SummarizationMiddleware                         [13]
│         + private data     → PIIMiddleware                                   [13]
│         + risky actions    → HumanInTheLoopMiddleware                        [14]
│         + custom behaviour → your own AgentMiddleware                        [15]
│
└─ You need control over the flow itself? (custom steps, branching, several agents,
   loops with your own rules, pause/resume of long jobs)
      └─► LangGraph: StateGraph + nodes + edges                                [16–19]
```

**Rule of thumb:** start at the simplest level that works, and move up only when you hit a limit.
Every step up adds flexibility, but also cost, latency and unpredictability.

---

## 2. Library by library: what it is, when to use it, why

### Raw provider SDK (`openai`, `google-genai`, …) [01–02]
- **Use when:** a tiny script, one provider forever, or you need a brand-new provider feature on day one.
- **Why not by default:** every provider has a different API, and you hand-write tool schemas, loops and parsing.

### LangChain: models, messages, prompts, tools [04–09]
- **Use when:** you call LLMs at all. It is the standard interface.
- **Why:** one API for every provider (`"openai:gpt-4o"` → `"groq:qwen/qwen3-32b"` is a one-string change),
  schemas generated from Python functions (`@tool`), structured output via Pydantic, streaming and batching built in.

### LangChain `create_agent` + middleware [10–15]
- **Use when:** the model should decide which tools to call, in a loop, until the task is done.
  This covers most agent use cases: Q&A over tools/DBs, assistants, research helpers.
- **Why:** it is a production-ready ReAct loop in one line. Cross-cutting needs (memory, summarisation,
  PII, approvals, limits, retries) are added as **middleware** instead of rewriting the loop.
- **Limit:** the shape is fixed (*model ⇄ tools*). If you need a different shape, go to LangGraph.

### LangGraph [16–19]
- **Use when:** you need to design the control flow yourself, for example:
  - a classifier node that routes to different specialised handlers;
  - a workflow with fixed steps **and** LLM decisions inside some steps;
  - multiple agents handing work to each other;
  - loops with custom stop rules (reflect → improve → check, at most 3 times);
  - long-running jobs that must persist, pause for a human and resume later.
- **Why:** explicit state + nodes + edges give you full control and visibility, with persistence
  (checkpointers) and interrupts built into the runtime.
- **Cost:** more code than `create_agent`. Don't use it for a plain tool-calling loop.

### LangSmith
- **Use when:** debugging or evaluating anything above. Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY`
  to see every LLM and tool call, the tokens used and the latency.

---

## 3. Side-by-side comparisons

### Chain vs. agent vs. graph
| | LCEL chain | `create_agent` | LangGraph |
|---|---|---|---|
| Who decides the steps | you | the model | you (structure) + model (inside nodes) |
| Shape | straight line | fixed loop *model ⇄ tools* | anything: branches, loops, parallel, sub-graphs |
| Code needed | tiny | small | most |
| Predictability | highest | lowest | you choose |
| Typical use | summarise, translate, extract | assistants, tool Q&A, SQL agent | complex / multi-agent / long-running systems |

### Memory options
| Need | Use | Notebook |
|---|---|---|
| Understand the basics | a Python list you resend each call | 08 |
| History inside a prompt template | `MessagesPlaceholder("history")` | 06 |
| Agent / graph remembers a conversation | `checkpointer=InMemorySaver()` + `thread_id` | 11, 18 |
| Memory that survives restarts | a persistent checkpointer (SQLite / Postgres packages) | (not covered yet) |
| Conversation too long | `SummarizationMiddleware` or trimming | 13 |

### Getting structured data back
| From | Use | Result |
|---|---|---|
| a model call | `model.with_structured_output(Schema)` | a `Schema` instance |
| an agent | `create_agent(..., response_format=Schema)` | `result["structured_response"]` |

### Middleware picker
| Problem | Middleware |
|---|---|
| Chat history grows too large / too expensive | `SummarizationMiddleware` |
| Emails, card numbers etc. must not reach the LLM | `PIIMiddleware` |
| A tool is dangerous (send, pay, delete) | `HumanInTheLoopMiddleware` |
| Logging, guardrails, rewriting replies | custom `AgentMiddleware` / `@before_model` / `@after_model` |
| Agent loops forever | `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware` |
| Provider outages / flaky calls | `ModelFallbackMiddleware`, `ModelRetryMiddleware`, `ToolRetryMiddleware` |

### Choosing a model provider (as used in this course)
| Need | Typical pick | Why |
|---|---|---|
| Reliable all-rounder, best tool calling | OpenAI `gpt-4o` / `gpt-4.1` | strong instruction following |
| Cheap helper tasks (summaries) | `gpt-4o-mini` | low cost, fast |
| Very fast / cheap open models | Groq (`qwen/qwen3-32b`, Llama) | fast inference hardware |
| Google ecosystem, multimodal | Gemini flash models | long context, images |

With `init_chat_model` you can switch providers anytime, so start with one and compare later.

---

## 4. Why each project is built the way it is

| Project | Built with | Why this choice |
|---|---|---|
| **19 Research chatbot** | LangGraph `StateGraph` + `ToolNode` | Built by hand **to learn** the loop. In real code `create_agent(model, tools)` would be enough, because the flow is the standard ReAct loop. |
| **21 SQL inventory agent** | `create_agent` + one `@tool` + `response_format` | The model must **write** SQL and may need several tries, so it's an agent. The flow is the standard loop, so LangGraph isn't needed. Structured output gives rows your code can use. The DB is read-only because the LLM writes the queries. |
| **22 Dynamic tool agent** | `create_agent` + `StructuredTool.from_function` + SQLite | Tools come from a database at runtime, so `@tool` (decorated at import time) can't be used. `StructuredTool.from_function` builds tools from data and gives each its own name and description. |

---

## 5. Common pitfalls (all hit during this course)
1. Hard-coding API keys in notebooks. Keep them in `.env` only.
2. Expecting the model to remember previous calls. LLMs are stateless; use history or a checkpointer.
3. Vague tool docstrings. The docstring **is** the tool's instructions for the model.
4. Returning the full message list from a LangGraph node. With `add_messages`, return only the new messages.
5. Adding a static edge to `END` next to `tools_condition`. Both paths then run.
6. Two tools with the same name. The model can't tell them apart.
7. Letting an LLM run arbitrary SQL or `exec()` code with write access. Use read-only connections and sandboxes.
8. Using an agent where a single call or chain would do. It is slower, costlier and less predictable.

---
✅ **Done with 20 When to use what.** Next: [21 Project: SQL agent →](../05_Projects/21_sql_inventory_agent/sql_agent.ipynb)
[🏠 Roadmap](../README.md)
