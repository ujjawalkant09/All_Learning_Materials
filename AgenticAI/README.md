# Agentic AI — From LLM Basics to LangChain, LangGraph & Projects

A single, linear course. **Start at step 1 and follow the "Next →" link at the bottom of every notebook.**
Each notebook opens with *What you'll learn* and ends with *Revision notes*. To revise quickly, read the
first and last cell of each one.

```
 Part 1 ──────────► Part 2 ───────────► Part 3 ───────────► Part 4 ──────► Part 5 ──────► Part 6 ──────► Part 7
 AI Fundamentals    LangChain           LangGraph           When to use    Projects       Exercises      RAG Mastery
 how LLMs & agents  models, tools,      graphs, state,      what & why                    drills +       BM25, hybrid,
 work               agents, middleware  custom agent loops                                capstone       rerank, agentic
 (01–03)            (04–15c)            (16–19)             (20)           (21–22)        (23–24)        (25–37)
```

---

## Setup (once)

```bash
cd AgenticAI
cp .env.example .env          # add your API keys here, the only place keys live
uv sync                       # creates/updates the single .venv in this folder (includes pytest for step 24)
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
| 15a | [Runtime context](02_LangChain/15a_runtime_context.ipynb) | `context_schema`, `ToolRuntime`, `@dynamic_prompt`, tools that read/update state with `Command`, context vs state vs store |
| 15b | [Streaming](02_LangChain/15b_streaming.ipynb) | `stream_mode` = values / updates / messages / custom, `runtime.stream_writer`, `ainvoke` / `astream`, FastAPI SSE |
| 15c | [RAG](02_LangChain/15c_rag.ipynb) | load → split → embed → vector store → retriever, MMR & filters, LCEL RAG chain, agentic RAG, hybrid search / re-ranking / evaluation |

## Part 3 · LangGraph: when you need control over the flow
| Step | Notebook | You'll learn |
|---|---|---|
| 16 | 🔌 [First graph](03_LangGraph/16_first_graph.ipynb) | **why LangGraph**, state, nodes, edges, conditional edges, `compile` |
| 17 | 🔌 [State & reducers](03_LangGraph/17_state_and_reducers.ipynb) | overwrite vs `operator.add` vs `add_messages`, `MessagesState` |
| 18 | [Tool-calling agent graph](03_LangGraph/18_tool_calling_agent_graph.ipynb) | ReAct loop by hand: `ToolNode`, `tools_condition`, extra state, memory, common mistakes, **streaming a graph** (`stream_mode`, `get_stream_writer`, `astream`) |
| 19 | [Research chatbot](03_LangGraph/19_research_chatbot_multiple_tools.ipynb) | arXiv + Wikipedia + Tavily tools in one graph, live progress with `stream_mode="updates"` |
| 20 | [Human-in-the-loop graph](03_LangGraph/20_human_in_loop_graph.ipynb) | `interrupt()` + `Command(resume=...)`, checkpointer + `thread_id`, `get_state().next`, pausing while streaming, common mistakes |

## Part 4 · When to Use What
| Step | Guide | You'll learn |
|---|---|---|
| 20 | [Choosing the right tool](04_When_To_Use_What/20_choosing_the_right_tool.md) | decision tree; raw SDK vs chain vs `create_agent` vs LangGraph; memory, middleware & model pickers; why each project is built the way it is; pitfalls |

## Part 5 · Projects
| Step | Project | Built with |
|---|---|---|
| 21 | [SQL inventory agent](05_Projects/21_sql_inventory_agent/) | `create_agent` + read-only SQL tool + structured output |
| 22 | [Dynamic tool agent](05_Projects/22_dynamic_tool_agent/) | agents and tool code loaded from SQLite, `StructuredTool` |

## Part 6 · Exercises: revise by doing
| Step | Exercise | What you do |
|---|---|---|
| 23 | 🔌 [Concept drills](06_Exercises/23_concept_drills.ipynb) | 15 small fill-in-the-TODO drills (one per concept) with auto-checks and hidden solutions, plus a "when to use what" quiz |
| 24 | [Capstone: AI expense assistant](06_Exercises/24_capstone_expense_assistant/) | build a real Python project in 8 milestones using **every** concept. 46 `pytest` tests tell you when each milestone is done; reference solution included |

Revising later? Redo step 23 (≈1 hour), then rebuild the capstone from the starter.

## Part 7 · RAG Mastery: RAG & agentic search in depth (interview-ready)
Module home: [07_RAG_Mastery/README.md](07_RAG_Mastery/README.md)

| Step | Guide / lab | You'll learn |
|---|---|---|
| 25 | [RAG: the big picture](07_RAG_Mastery/25_rag_big_picture.md) | two pipelines, retrieval funnel, naive → advanced → agentic, RAG vs fine-tuning vs long context |
| 26 | [Ingestion & chunking](07_RAG_Mastery/26_ingestion_and_chunking.md) | parsing, tables, metadata, chunking strategies, parent-child, contextual retrieval, index freshness |
| 27 | [Embeddings & vector search](07_RAG_Mastery/27_embeddings_and_vector_search.md) | bi-encoders, choosing models, HNSW / IVF / PQ, vector DBs, filtering, dense weak spots |
| 28 | [BM25 & Elasticsearch](07_RAG_Mastery/28_bm25_and_elasticsearch.md) | inverted index, analyzers, BM25 step by step, ES mappings / query DSL / kNN / hybrid, SPLADE |
| 29 | [Hybrid search & reranking](07_RAG_Mastery/29_hybrid_search_and_reranking.md) | RRF, bi- vs cross-encoder, ColBERT, LLM rerankers, MMR, lost in the middle |
| 30 | [Query transformation & routing](07_RAG_Mastery/30_query_transformation_and_routing.md) | rewrite, multi-query, HyDE, decomposition, step-back, self-query, routers |
| 31 | [RAG problems & fixes](07_RAG_Mastery/31_rag_problems_and_fixes.md) | debugging ladder, 7 failure points, 40+ problems → fixes, hallucination, security |
| 32 | [Agentic RAG & agentic search](07_RAG_Mastery/32_agentic_rag_and_agentic_search.md) | CRAG, Self-RAG, Adaptive RAG, multi-hop, deep research, GraphRAG, tool design |
| 33 | [Evaluation & production](07_RAG_Mastery/33_evaluation_and_production.md) | Recall@k, MRR, nDCG, faithfulness, RAGAS, latency, caching, ACLs, monitoring |
| 34 | [Interview questions](07_RAG_Mastery/34_interview_questions.md) | 70 Q&A with hidden answers + rapid-fire revision |
| 35 | 🔌 [Lab: search engine from scratch](07_RAG_Mastery/35_lab_search_from_scratch.ipynb) | BM25, RRF, MMR and retrieval metrics in plain Python |
| 36 | [Lab: hybrid + rerank pipeline](07_RAG_Mastery/36_lab_hybrid_rerank_pipeline.ipynb) | BM25 vs dense vs hybrid vs cross-encoder, measured per question (no API key) |
| 37 | [Lab: agentic RAG with LangGraph](07_RAG_Mastery/37_lab_agentic_rag_langgraph.ipynb) | CRAG graph, search agent with ACL, adaptive router |

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

# Agent                                                          [10-15b]
agent = create_agent(model, tools, system_prompt=..., response_format=...,
                     checkpointer=InMemorySaver(), middleware=[...], context_schema=Ctx)
agent.invoke({"messages": [...]}, {"configurable": {"thread_id": "1"}}, context=Ctx(user_id="u1"))  # -> dict
def my_tool(q: str, runtime: ToolRuntime[Ctx]): runtime.context.user_id   # hidden from the model
for token, meta in agent.stream(inp, stream_mode="messages"): ...           # also values/updates/custom

# RAG                                                            [15c]
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
retriever = InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings()).as_retriever(search_kwargs={"k": 3})

# Hybrid RAG                                                     [25-37]
fused = rrf([bm25_ids, dense_ids])                              # Σ 1/(60 + rank)
top5 = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2").predict([(q, doc) for doc in top50])  # rerank

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
├── 02_LangChain/            steps 04–15c
├── 03_LangGraph/            steps 16–20
├── 04_When_To_Use_What/     step 20
├── 05_Projects/             steps 21–22
├── 06_Exercises/            steps 23–24
└── 07_RAG_Mastery/          steps 25–37
```
