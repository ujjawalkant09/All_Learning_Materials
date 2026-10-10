# Agentic AI — From LLM Basics to LangChain, LangGraph & Projects

A single, linear course. **Start at step 1 and follow the "Next →" link at the bottom of every notebook.**
Each notebook opens with *What you'll learn* and ends with *Revision notes*. To revise quickly, read the
first and last cell of each one.

```
 Part 1 ─────────────► Part 2 ──────────────► Part 3 ──────────────► Part 4 ─────────► Part 5
 AI Fundamentals       LangChain               LangGraph               When to use      Projects
 how LLMs & agents     models, tools,          graphs, state,          what & why
 work                  agents, middleware      custom agent loops
 (01–03)               (04–15)                 (16–19)                 (20)             (21–22)
```

---

## Setup (once)

```bash
cd AgenticAI
cp .env.example .env          # add your API keys here, the only place keys live
uv sync                       # creates/updates the single .venv in this folder
```

In VS Code / Jupyter pick the kernel **`AgenticAI/.venv`**. It is shared by every notebook in every folder.
Every notebook calls `load_dotenv()`, which walks up the folders and finds this one `.env`.

| Key | Needed for |
|---|---|
| `OPENAI_API_KEY` | almost every notebook |
| `GROQ_API_KEY` | 04, 05 |
| `GOOGLE_API_KEY` | 04 (Gemini) |
| `TAVILY_API_KEY` | 19 (web search) |

🔌 = runs offline, no API key needed.

---

## Part 1 · AI Fundamentals: understand what you're building on
| Step | Notebook | You'll learn |
|---|---|---|
| 01 | [How LLMs work](01_AI_Fundamentals/01_how_llms_work.ipynb) | next-token prediction, tokens, context window, temperature, roles, providers & keys, raw OpenAI SDK call, statelessness, limitations |
| 02 | [From LLMs to agents](01_AI_Fundamentals/02_from_llms_to_agents.ipynb) | the ladder: call → chain → tool calling → agent → graph; tool calling by hand; ReAct loop; workflow vs agent; LangChain vs LangGraph vs LangSmith |
| 03 | 🔌 [Python prerequisites](01_AI_Fundamentals/03_python_prerequisites.ipynb) | Pydantic models & validation, `TypedDict`, `Literal`, `Annotated` |

## Part 2 · LangChain: the standard toolkit for LLM apps
| Step | Notebook | You'll learn |
|---|---|---|
| 04 | [Chat models & providers](02_LangChain/04_chat_models_and_providers.ipynb) | **why LangChain**, `init_chat_model`, OpenAI / Gemini / Groq, `invoke` / `stream` / `batch` |
| 05 | [Messages](02_LangChain/05_messages.ipynb) | `SystemMessage`, `HumanMessage`, `AIMessage`, dict format, token usage |
| 06 | [Prompt templates & chains](02_LangChain/06_prompt_templates_and_chains.ipynb) | `PromptTemplate`, `ChatPromptTemplate`, `MessagesPlaceholder`, LCEL `prompt \| model \| parser` |
| 07 | [Structured output](02_LangChain/07_structured_output.ipynb) | `with_structured_output(PydanticModel)` |
| 08 | [Conversation history](02_LangChain/08_conversation_history.ipynb) | memory by hand: resending history |
| 09 | [Tools & tool calling](02_LangChain/09_tools_and_tool_calling.ipynb) | `@tool`, `bind_tools`, `tool_calls`, the manual tool loop |
| 10 | [First agent](02_LangChain/10_first_agent.ipynb) | `create_agent`: the loop automated |
| 11 | [Agent memory](02_LangChain/11_agent_memory.ipynb) | checkpointer + `thread_id` |
| 12 | [Agent structured output](02_LangChain/12_agent_structured_output.ipynb) | `response_format`, `structured_response` |
| 13 | [Middleware: summarization & PII](02_LangChain/13_middleware_summarization_and_pii.ipynb) | middleware lifecycle, message / token / fraction triggers, redact / mask |
| 14 | [Human-in-the-loop](02_LangChain/14_human_in_the_loop.ipynb) | interrupts; approve / edit / reject with `Command(resume=...)` |
| 15 | [Custom middleware](02_LangChain/15_custom_middleware.ipynb) | `AgentMiddleware` hooks, decorator middleware, other built-ins |

## Part 3 · LangGraph: when you need control over the flow
| Step | Notebook | You'll learn |
|---|---|---|
| 16 | 🔌 [First graph](03_LangGraph/16_first_graph.ipynb) | **why LangGraph**, state, nodes, edges, conditional edges, `compile` |
| 17 | 🔌 [State & reducers](03_LangGraph/17_state_and_reducers.ipynb) | overwrite vs `operator.add` vs `add_messages`, `MessagesState` |
| 18 | [Tool-calling agent graph](03_LangGraph/18_tool_calling_agent_graph.ipynb) | ReAct loop by hand: `ToolNode`, `tools_condition`, extra state, memory, common mistakes |
| 19 | [Research chatbot](03_LangGraph/19_research_chatbot_multiple_tools.ipynb) | arXiv + Wikipedia + Tavily tools in one graph |

## Part 4 · When to Use What
| Step | Guide | You'll learn |
|---|---|---|
| 20 | [Choosing the right tool](04_When_To_Use_What/20_choosing_the_right_tool.md) | decision tree; raw SDK vs chain vs `create_agent` vs LangGraph; memory, middleware & model pickers; why each project is built the way it is; pitfalls |

## Part 5 · Projects
| Step | Project | Built with |
|---|---|---|
| 21 | [SQL inventory agent](05_Projects/21_sql_inventory_agent/) | `create_agent` + read-only SQL tool + structured output |
| 22 | [Dynamic tool agent](05_Projects/22_dynamic_tool_agent/) | agents and tool code loaded from SQLite, `StructuredTool` |

---

## Cheat sheet

```python
# Model                                                          [04-07]
model = init_chat_model("openai:gpt-4o")                        # .invoke() -> AIMessage
model.stream(...); model.batch([...])
model.with_structured_output(MySchema)                          # -> MySchema instance
chain = prompt | model | StrOutputParser()                      # LCEL

# Tools                                                          [09]
@tool
def get_weather(city: str) -> str:
    "Docstring = instructions for the model."
model.bind_tools([get_weather])                                 # -> response.tool_calls

# Agent                                                          [10-15]
agent = create_agent(model, tools, system_prompt=..., response_format=...,
                     checkpointer=InMemorySaver(), middleware=[...])
agent.invoke({"messages": [...]}, {"configurable": {"thread_id": "1"}})   # -> dict

# Graph                                                          [16-19]
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
g = StateGraph(State)
g.add_node("llm", llm_node); g.add_node("tools", ToolNode(tools))
g.add_edge(START, "llm"); g.add_conditional_edges("llm", tools_condition); g.add_edge("tools", "llm")
graph = g.compile(checkpointer=InMemorySaver())
```

## Folder layout
```
AgenticAI/
├── README.md                ← you are here
├── .env / .env.example      ← API keys (one file for everything)
├── .venv/                   ← one shared Python environment
├── pyproject.toml, uv.lock, requirements.txt
├── 01_AI_Fundamentals/      steps 01–03
├── 02_LangChain/            steps 04–15
├── 03_LangGraph/            steps 16–19
├── 04_When_To_Use_What/     step 20
└── 05_Projects/             steps 21–22
```

**Coming next:** RAG (retrieval-augmented generation). Its libraries (`pypdf`, `pymupdf`, `sentence-transformers`,
`faiss-cpu`, `chromadb`, `typesense`) are already in `pyproject.toml`. Add it as `06_RAG/`.
