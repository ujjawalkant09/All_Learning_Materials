**Part 7 · RAG Mastery** · step 32 of 37
[← 31 RAG problems & fixes](31_rag_problems_and_fixes.md) · [🏠 Roadmap](../README.md) · [33 Evaluation & production →](33_evaluation_and_production.md)

# 32 · Agentic RAG & Agentic Search

> **What you'll learn:** what makes RAG "agentic", the main patterns (**ReAct retrieval**, **Router**,
> **Corrective RAG**, **Self-RAG**, **Adaptive RAG**, **multi-hop / iterative**, **Deep Research** with
> sub-agents, **GraphRAG**), how to design good search tools for agents, "agentic search" without vectors
> (grep/file navigation), stopping rules, and agent-specific failure modes. Code in LangGraph.

---

## 1. From pipeline to agent

```
 2-STEP RAG (pipeline)                         AGENTIC RAG (loop)
 ─────────────────────                         ──────────────────
 question → retrieve → generate                 question
 always 1 search, raw question                      │
 fixed path, cheap, predictable                     ▼
                                              ┌─► THINK: do I need info? what should I search?
                                              │      │
                                              │      ▼
                                              │   ACT: call a tool (search docs / SQL / web / fetch doc)
                                              │      │
                                              │      ▼
                                              │   OBSERVE: read results. Enough? Relevant?
                                              └──────┤ no → refine query, try another source
                                                     │ yes
                                                     ▼
                                                  ANSWER with citations
```

**Agentic = the LLM decides the retrieval steps** (if, what, where, how many times, when to stop).
**Memory hook: "Think → Search → Read → Decide (repeat) → Answer."**

| | 2-step RAG | Agentic RAG |
|---|---|---|
| Searches | exactly 1 | 0..N, decided by the model |
| Query | user's words | rewritten / decomposed by the model |
| Sources | one index | many tools (docs, SQL, web, APIs) |
| Self-correction | none | grades results, retries |
| Latency / cost | low, predictable | higher, variable |
| Best for | FAQ, simple lookups | multi-part, multi-hop, research, ambiguous questions |

**Rule:** start with 2-step RAG. Go agentic when evals show multi-hop / multi-source / ambiguous questions failing.

---

## 2. The patterns (know each in one sentence + a diagram)

### 2.1 Retrieval as a tool (ReAct agent) ✅ simplest agentic RAG
Give the agent a `search_docs(query)` tool. The model decides when to call it and with what query.
Already built in [15c](../02_LangChain/15c_rag.ipynb) with `create_agent`.

### 2.2 Router RAG
An LLM (or classifier) picks **one** source: vector index A / index B / SQL / web / none. Cheap "agentic-lite". See [30](30_query_transformation_and_routing.md).

### 2.3 Corrective RAG (CRAG) ✅ very popular interview topic
**Grade the retrieved docs before answering.** If they're bad, fix the search.

```
 question → retrieve → GRADE each doc (relevant? yes/no)
                          │
          ┌───────────────┼──────────────────────────┐
     all relevant     some relevant              none relevant
          │               │                           │
          ▼               ▼                           ▼
       generate     keep good ones +           REWRITE query → search again
                    supplement (web / 2nd       (or web search fallback)
                    index)                            │
                                                      ▼
                                                  generate
```
Analogy: a student checks **"do these pages actually answer the question?"** before writing, and goes back to the library if not.

### 2.4 Self-RAG (self-reflective RAG)
The model **critiques itself** at several points:
1. *Do I need to retrieve?* (retrieve / don't)
2. *Is this passage relevant?*
3. *Is my answer supported by the passage?* (grounded / partially / not)
4. *Is my answer useful?*
The original paper trained special "reflection tokens"; in practice we implement the same checks with LLM-judge nodes in a graph.

```
 retrieve → generate → [grounded in docs?] ── no ──► regenerate (or retrieve again)
                             │ yes
                             ▼
                     [answers the question?] ── no ──► rewrite query → retrieve
                             │ yes
                             ▼
                          answer
```

### 2.5 Adaptive RAG
**Pick the strategy by question difficulty:**
- simple / general knowledge → answer directly (no retrieval)
- single-fact → one-shot RAG
- complex / multi-hop → iterative agentic RAG
A small classifier/LLM decides first. Saves cost on easy questions, spends effort on hard ones.

### 2.6 Iterative / multi-hop retrieval
Retrieve → read → use what you learned to form the **next** query (IRCoT = interleave chain-of-thought with retrieval).
```
Q: "What's the on-call policy of the team that owns NimbusDB?"
 hop 1: search "NimbusDB owner team"         → "Owned by the Storage team"
 hop 2: search "Storage team on-call policy" → "Storage on-call: 1 week rotation..."
 answer
```

### 2.7 Plan-and-execute / Deep Research ✅ the "agentic search" frontier
For big research questions: a **planner** writes a plan of sub-questions, **worker sub-agents** search in parallel
(each with its own context window), a **synthesiser** merges findings into a cited report.

```
                   ┌──► sub-agent 1: "EU AI Act obligations for providers"  ──┐
 question ─► PLAN ─┼──► sub-agent 2: "US state AI laws 2026"                ──┼─► SYNTHESISE ─► report + citations
                   └──► sub-agent 3: "India AI regulation status"           ──┘        │
                                                                                       └─► gaps found? → more research
```
Why sub-agents: each one gets a **clean, focused context** (no clutter from others), they run **in parallel**,
and the orchestrator only sees their **compressed findings**. Cost: many more tokens. Use for high-value questions.

### 2.8 GraphRAG / knowledge-graph RAG
Extract **entities and relations** from docs into a graph (`NimbusDB —owned_by→ Storage team —led_by→ Priya`).
- **Local search:** start from entities in the question, walk relations (great for multi-hop "who/what is connected").
- **Global search:** cluster the graph into **communities**, pre-write summaries per community, answer "what are the main themes?" from summaries (vector top-k can't answer global questions).
- Cost: expensive LLM extraction at index time; graph quality matters. Microsoft GraphRAG, LightRAG, Neo4j are names to know.

### 2.9 Agentic search without vectors ("grep and navigate")
Coding agents (like Claude Code) often **don't use a vector index** for code. They use tools like `grep`, `glob`,
`list_dir`, `read_file` and **iterate** like a human developer: search a symbol, open the file, follow imports.
- Pros: always fresh (no index to sync), exact, follows structure, no chunking problems.
- Cons: more tool calls/tokens, needs a capable model, slow on huge unstructured corpora.
- Lesson: **"retrieval" doesn't have to mean "vector DB".** Give the agent the right navigation tools for the data shape.

---

## 3. Designing tools for an agentic search system

The agent is only as good as its tools. Good tool design is half the job.

| Principle | Example |
|---|---|
| **Clear name + docstring** (the model reads it to decide) | `search_hr_policies(query)`: "Search HR policies (leave, benefits, conduct). Use short keyword queries." |
| **Few, distinct tools** (overlapping tools confuse the model) | `search_docs`, `run_sql`, `web_search`, not 12 similar search tools |
| **Return compact, cited results** | `[doc_id=hr-7 | leave_policy.pdf p.3] Full-time employees get 24 days...` (snippets, not whole docs) |
| **Search + fetch pair** | `search(query) → ids + snippets`, then `fetch(doc_id)` for the full text only when needed (saves tokens) |
| **Expose filters as parameters** | `search_docs(query: str, department: Literal["HR","IT"] | None, year_from: int | None)` |
| **Helpful errors** | "No results. Try fewer words or remove the year filter." → the model can recover |
| **Security inside the tool** | the tool applies the user's ACL from **runtime context**, the model can't override it |
| **Budget** | max results per call, max characters returned |

```python
from langchain.tools import tool, ToolRuntime

@tool
def search_docs(query: str, department: str | None = None, runtime: ToolRuntime = None) -> str:
    """Search internal company documents (HR, IT, Finance, Product). Use short, specific keyword queries.
    Returns up to 5 snippets with [doc_id] for citation. Call again with a different query if results are weak."""
    user_groups = runtime.context.groups                      # ACL comes from trusted context, NOT from the model
    hits = hybrid_search(query, filters={"department": department, "allowed_groups": user_groups}, k=5)
    if not hits:
        return "No results. Try a broader query or remove the department filter."
    return "\n\n".join(f"[{h.id} | {h.source}] {h.text[:500]}" for h in hits)
```

---

## 4. Stopping, budgets & control (agents must know when to stop)

| Risk | Control |
|---|---|
| Infinite search loops | **max iterations** (e.g. 3 rewrites, 8 tool calls); LangGraph `recursion_limit` |
| Over-searching easy questions | adaptive routing; prompt "search only if needed" |
| Query drift (each rewrite moves further from the question) | always rewrite from the **original** question + feedback |
| Context bloat (tool results pile up) | snippets not full docs; summarise old tool results; sub-agents |
| Cost/latency explosion | token/time budget in state; cheaper model for grading/rewriting |
| Never says "I don't know" | after N failed attempts, answer "not found" with what was tried |

**Workflow or agent?** If you can draw the steps (retrieve → grade → rewrite → retry) → build it as a **LangGraph
workflow** (predictable, testable). If you can't predict the steps → a **ReAct agent**. CRAG/Self-RAG are usually built
as graphs with LLM decisions at the edges: the best of both.

---

## 5. Corrective RAG in LangGraph (skeleton)

Full runnable version: [37 Lab: agentic RAG with LangGraph](37_lab_agentic_rag_langgraph.ipynb).

```python
class State(TypedDict):
    question: str          # original question (never overwritten → no query drift)
    query: str             # current search query
    docs: list[Document]
    attempts: int
    answer: str

def retrieve(state):       return {"docs": retriever.invoke(state["query"])}
def grade(state):          # keep only docs an LLM judge marks relevant
    keep = [d for d in state["docs"] if grader.invoke({"q": state["question"], "doc": d.page_content}).relevant]
    return {"docs": keep}
def rewrite(state):        return {"query": rewriter.invoke(state["question"]), "attempts": state["attempts"] + 1}
def generate(state):       return {"answer": rag_chain.invoke({"question": state["question"], "docs": state["docs"]})}

def decide(state) -> str:
    if state["docs"]:              return "generate"
    if state["attempts"] >= 2:     return "give_up"
    return "rewrite"

g = StateGraph(State)
g.add_node("retrieve", retrieve); g.add_node("grade", grade); g.add_node("rewrite", rewrite)
g.add_node("generate", generate); g.add_node("give_up", lambda s: {"answer": "I couldn't find this in the documents."})
g.add_edge(START, "retrieve"); g.add_edge("retrieve", "grade")
g.add_conditional_edges("grade", decide, ["generate", "rewrite", "give_up"])
g.add_edge("rewrite", "retrieve"); g.add_edge("generate", END); g.add_edge("give_up", END)
graph = g.compile()
```

---

## 6. Evaluating agentic RAG (more than final answers)

- **Final answer** quality: correctness, faithfulness, citations (same as normal RAG, step 33).
- **Trajectory**: did it call the right tools, with good queries, in a reasonable number of steps?
- **Efficiency**: tool calls, tokens, latency per question. Track the distribution, not only the average.
- **Robustness**: does it stop? does it abstain correctly when nothing is found?
- Use tracing (LangSmith) to inspect every step.

---

## Revision notes
- Agentic RAG = LLM controls retrieval: **Think → Search → Read → Decide (repeat) → Answer**.
- Patterns: **ReAct tool**, **Router**, **CRAG** (grade docs → rewrite / web fallback), **Self-RAG** (retrieve? relevant? grounded? useful?), **Adaptive** (strategy by difficulty), **multi-hop** (IRCoT), **Deep Research** (plan → parallel sub-agents → synthesise), **GraphRAG** (local walk + global community summaries), **grep-style agentic search**.
- Tools: clear docstrings, few & distinct, **search + fetch**, compact cited snippets, filters as params, helpful errors, **ACL inside the tool from trusted context**.
- Control: max iterations, budgets, rewrite from original question, abstain after N fails.
- Drawable steps → LangGraph workflow; unpredictable steps → agent.
- Evaluate answers **and** trajectories **and** cost.

---
✅ **Done with 32.** Next: [33 Evaluation & production →](33_evaluation_and_production.md)
