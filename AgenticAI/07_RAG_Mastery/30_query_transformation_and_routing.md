**Part 7 · RAG Mastery** · step 30 of 37
[← 29 Hybrid search & reranking](29_hybrid_search_and_reranking.md) · [🏠 Roadmap](../README.md) · [31 RAG problems & fixes →](31_rag_problems_and_fixes.md)

# 30 · Query Transformation & Routing: Fix the Question Before You Search

> **What you'll learn:** why users' questions are bad search queries, and the toolbox to fix them:
> conversational rewriting, multi-query, RAG-Fusion, **HyDE**, decomposition, step-back prompting,
> self-query (metadata filter extraction), and **routing** to the right data source.

---

## 1. Why transform the query?

Users write questions for **humans**, not for search engines:

| User says | Problem |
|---|---|
| "and what about for interns?" | depends on chat history; alone it's meaningless |
| "my thing is broken after the update pls help" | vague, no keywords |
| "Compare the leave policy of India and US offices and tell me which gives more days" | 2+ searches needed |
| "VPN docs from 2025 by the security team" | contains **filters**, not just meaning |
| "What's 2+2?" | needs no search at all |

**Memory hook: "Rewrite, Expand, Split, Filter, Route" (R-E-S-F-R).**

---

## 2. The techniques

### 2.1 Conversational rewrite (condense question) ✅ must-have for chatbots
Turn a follow-up into a **standalone** query using the chat history.
```
History:  "How many leave days do full-time employees get?" → "24 days."
User:     "and interns?"
Rewrite:  "How many paid leave days do interns get at Nimbus Labs?"
```
Without this, follow-up questions retrieve garbage. Search with the rewrite, but answer the original question with history.

### 2.2 Query rewriting / clarification
LLM turns a messy question into a clean search query (add keywords, remove chit-chat, fix typos).
If the question is **too ambiguous**, the best move is often to **ask the user** a clarifying question (agents can do this).

### 2.3 Multi-query (expansion)
Generate 3–5 different phrasings, retrieve for each, merge (union or RRF).
```
"How do I get reimbursed for internet?" →
  1. "internet allowance reimbursement policy"
  2. "remote work expense claim home broadband"
  3. "monthly internet bill refund process"
```
Fixes vocabulary mismatch. Costs: 1 LLM call + N searches. LangChain: `MultiQueryRetriever`.

**RAG-Fusion** = multi-query + **RRF** to merge the lists (docs found by several phrasings win).

### 2.4 HyDE (Hypothetical Document Embeddings)
**Questions and answers look different.** A short question's vector is not that close to a long, formal answer's vector.
HyDE: ask the LLM to **write a fake answer**, then embed the fake answer and search with it.

```
Q: "Can I carry over unused leave?"
LLM fake answer: "Employees may carry over a limited number of unused annual leave days to the next
                  calendar year; days above the limit expire..."   (facts may be wrong, doesn't matter!)
→ embed this → search → finds the real policy paragraph (answer-to-answer similarity is high)
```
- Good for: short/vague questions, zero-shot domains.
- Risk: if the LLM knows nothing about the topic, the fake answer can point in the wrong direction. Adds an LLM call of latency.
- **Memory hook: "HyDE = search with a fake answer to find the real one."**

### 2.5 Decomposition (sub-questions) ✅ for multi-part / multi-hop
Split a complex question into simple ones, retrieve for each, then combine.
```
"Which office gives more leave days, India or US, and how much more?"
  → q1: "annual leave days India office"
  → q2: "annual leave days US office"
  → answer: compare
```
- **Parallel** decomposition: sub-questions are independent (above).
- **Sequential** (multi-hop): the answer of q1 is needed to ask q2. "Who manages the team that owns NimbusDB, and what is their on-call policy?" → find team → find manager → find policy. This is where **agents** shine (step 32).

### 2.6 Step-back prompting
Ask a more **general** question first, retrieve background, then answer the specific one.
```
Specific:  "Why did my pod get OOMKilled with limit 512Mi on node X?"
Step-back: "How do Kubernetes memory limits and OOMKill work?"
```
Retrieve for both → the LLM gets principles + specifics.

### 2.7 Self-query / metadata filter extraction ✅ very practical
Let an LLM extract **structured filters** from the question, and search only with the semantic part.
```
"VPN docs from 2025 by the security team"
→ { "query": "VPN", "filters": { "department": "security", "year": 2025 } }
```
Use **structured output** (Pydantic) so the result is always valid:

```python
from pydantic import BaseModel, Field
from typing import Literal

class SearchPlan(BaseModel):
    query: str = Field(description="keywords to search, without filter words")
    department: Literal["HR", "IT", "Finance", "Product"] | None = None
    year_from: int | None = None

plan = model.with_structured_output(SearchPlan).invoke(user_question)
```
Validate the filter values against an allow-list. Never let the LLM write raw filter code/SQL that you execute blindly.

### 2.8 Spelling, acronyms, synonyms (no LLM needed)
A glossary that expands internal acronyms ("PTO" → "paid time off", "SRE" → "site reliability") fixes many BM25 misses cheaply.

---

## 3. Routing: where should this question go?

Real systems have many sources: several vector indexes, a SQL database, an API, the web, or "just answer".

```
                         ┌──► "hi / thanks / what can you do"       → answer directly, no retrieval
                         ├──► policy / how-to questions             → docs index (hybrid search)
 question ──► ROUTER ────┼──► numbers / aggregates ("sales in Q2")  → SQL (text-to-SQL tool)
                         ├──► code questions                        → code index
                         ├──► recent news                           → web search
                         └──► out of scope / unsafe                 → polite refusal
```

How to build a router:
| Approach | Pros | Cons |
|---|---|---|
| **Rules / keywords** | free, predictable | brittle |
| **Embedding similarity to route examples** ("semantic router") | fast, cheap | needs examples per route |
| **Small classifier** | fast, accurate | needs labelled data |
| **LLM with structured output** (`Literal["docs","sql","web","none"]`) | flexible, no training | +1 LLM call |
| **Agent with tools** (each source = a tool) | most flexible; can use several | slowest, least predictable |

---

## 4. Which technique, when? (cheat table)

| Symptom | Technique |
|---|---|
| Follow-up questions fail | Conversational rewrite |
| Right doc uses different words | Multi-query / RAG-Fusion, synonyms, hybrid |
| Short vague questions | HyDE, or ask a clarifying question |
| Questions with 2+ parts | Decomposition |
| Needs chained lookups | Sequential decomposition → agent |
| Needs background knowledge | Step-back |
| Question contains dates/teams/types | Self-query filters |
| Multiple sources | Router |

**Cost reminder:** every technique adds an LLM call (latency + money). Turn them on based on **measured** failures, not because they exist. A cheap trick: run a fast first search; only if the top reranker score is low, apply heavier transformations (this is the idea behind **adaptive RAG**, step 32).

---

## Revision notes
- Users write for humans; search engines need clean, specific queries → transform first.
- Hook **R-E-S-F-R**: **R**ewrite (conversational, clarification), **E**xpand (multi-query, RAG-Fusion, HyDE, synonyms), **S**plit (decomposition, step-back), **F**ilter (self-query via structured output), **R**oute (to the right source).
- **HyDE = search with a fake answer to find the real one.**
- Multi-hop (answer of step 1 needed for step 2) → sequential decomposition → agents.
- Router options: rules → semantic router → classifier → LLM structured output → agent with tools.
- Every transformation costs a call; enable by measured need, or adaptively.

---
✅ **Done with 30.** Next: [31 RAG problems & fixes →](31_rag_problems_and_fixes.md)
