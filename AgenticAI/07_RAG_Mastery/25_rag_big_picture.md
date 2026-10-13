**Part 7 · RAG Mastery** · step 25 of 37
[← RAG module home](README.md) · [🏠 Roadmap](../README.md) · [26 Ingestion & chunking →](26_ingestion_and_chunking.md)

# 25 · RAG: The Big Picture

> **What you'll learn:** what RAG is, why it exists, the two pipelines (indexing and querying), every
> component by name, and when to use RAG vs fine-tuning vs long context.
> If you only remember one page from this module, remember this one.

---

## 1. The one-line idea

**RAG = Retrieval-Augmented Generation = "open-book exam" for an LLM.**

- A normal LLM answers from memory (its training data). Like a student in a **closed-book** exam.
- A RAG system first **looks up** the right pages in a book (your documents), then answers **using those pages**.
  Like a student in an **open-book** exam.

```
Without RAG:  Question ─────────────────────────────► LLM ──► answer from memory (may be old / wrong / made up)

With RAG:     Question ──► SEARCH your documents ──► top chunks ──► LLM ──► answer based on the chunks + citations
                           (the "R")                (the "A")      (the "G")
```

**R**etrieval = find relevant text. **A**ugmented = add that text to the prompt. **G**eneration = the LLM writes the answer.

---

## 2. Why do we need RAG? (the 5 problems it solves)

| Problem with a plain LLM | How RAG fixes it |
|---|---|
| **Doesn't know private data** (your HR policy, your code, your tickets) | We put the private text in the prompt at question time |
| **Knowledge cutoff** (doesn't know last week's news) | Update the index, not the model. New doc → searchable in minutes |
| **Hallucination** (confidently invents facts) | "Answer only from the context" + citations you can check |
| **No sources** (can't say where a fact came from) | Every chunk has metadata (file, page, URL) → we show citations |
| **Can't fit everything in the prompt** (1M docs ≫ context window) | Only send the 5–10 most relevant chunks |

Memory trick: **"P-F-H-S-S"** → **P**rivate, **F**resh, **H**allucination, **S**ources, **S**cale.

---

## 3. The two pipelines (most important diagram in the module)

Every RAG system has **two** separate pipelines. Interviewers love to ask you to draw this.

```
══════════════════ 1) INDEXING PIPELINE (offline, runs when documents change) ══════════════════

  Sources            Load/Parse          Clean            Chunk            Embed               Store
 ┌─────────┐       ┌──────────┐      ┌──────────┐     ┌─────────┐     ┌──────────┐      ┌────────────────────┐
 │PDF, HTML│──────►│ text +   │─────►│ remove   │────►│ split   │────►│ text →   │─────►│ Vector DB (dense)  │
 │Docs, DB │       │ metadata │      │ headers, │     │ into    │     │ vector   │      │ + Keyword index    │
 │Confluence│      │ tables   │      │ dupes    │     │ chunks  │     │ [0.1,..] │      │   (BM25, sparse)   │
 └─────────┘       └──────────┘      └──────────┘     └─────────┘     └──────────┘      └────────────────────┘

══════════════════ 2) QUERY PIPELINE (online, runs for every user question) ══════════════════

  User question
       │
       ▼
 ┌─────────────┐   ┌──────────────────────┐   ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌───────────┐
 │ Query       │──►│ Retrieve (top 50)    │──►│ Fuse     │──►│ Re-rank    │──►│ Build    │──►│ LLM       │──► answer
 │ transform   │   │  • dense (vectors)   │   │ (RRF)    │   │ (cross-    │   │ prompt   │   │ generates │   + citations
 │ (rewrite,   │   │  • sparse (BM25)     │   │          │   │  encoder)  │   │ with top │   │           │
 │  HyDE, ...) │   │  • metadata filters  │   │          │   │ → top 5    │   │ 5 chunks │   │           │
 └─────────────┘   └──────────────────────┘   └──────────┘   └────────────┘   └──────────┘   └───────────┘
```

**Memory trick for the query pipeline: "T-R-F-R-G"** → **T**ransform, **R**etrieve, **F**use, **R**erank, **G**enerate.
Say it as: *"Try Really Fast, Rank Good."*

### Why this order? The "funnel" idea

```
 1,000,000 chunks
      │   cheap + fast search (BM25 / vector ANN)     ~10–50 ms
      ▼
    50 candidates                    ← high RECALL: "is the right answer somewhere in here?"
      │   expensive + accurate (cross-encoder)        ~50–300 ms
      ▼
     5 chunks                        ← high PRECISION: "are the top ones really the best?"
      │   very expensive (LLM)                        ~1–5 s
      ▼
   1 answer
```

**Rule:** cheap methods on many items, expensive methods on few items. That's the whole architecture.

---

## 4. Every component, in one sentence

| Component | One-line job | Deep dive |
|---|---|---|
| **Loader / parser** | Turn PDF/HTML/DOCX/tables into clean text + metadata | [26](26_ingestion_and_chunking.md) |
| **Chunker** | Cut long text into pieces small enough to search, big enough to make sense | [26](26_ingestion_and_chunking.md) |
| **Embedding model** | Turn text into a vector so "similar meaning = nearby vectors" | [27](27_embeddings_and_vector_search.md) |
| **Vector database** | Store vectors and find the nearest ones fast (ANN, e.g. HNSW) | [27](27_embeddings_and_vector_search.md) |
| **Keyword index (BM25)** | Find chunks that contain the exact words (names, codes, IDs) | [28](28_bm25_and_elasticsearch.md) |
| **Elasticsearch / OpenSearch** | A search engine that does BM25 + vectors + filters at scale | [28](28_bm25_and_elasticsearch.md) |
| **Hybrid search + RRF** | Combine keyword and vector results into one list | [29](29_hybrid_search_and_reranking.md) |
| **Re-ranker (cross-encoder)** | Re-score the top 50 carefully and keep the best 5 | [29](29_hybrid_search_and_reranking.md) |
| **Query transformer** | Rewrite a bad user question into good search queries | [30](30_query_transformation_and_routing.md) |
| **Router** | Decide *where* to search (which index, SQL, web, or nothing) | [30](30_query_transformation_and_routing.md) |
| **Generator (LLM)** | Write the answer using only the given chunks, with citations | [31](31_rag_problems_and_fixes.md) |
| **Agent** | Loop: think → search → read → search again → answer | [32](32_agentic_rag_and_agentic_search.md) |
| **Evaluator** | Measure retrieval quality + answer quality, catch regressions | [33](33_evaluation_and_production.md) |

---

## 5. Two kinds of search: dense vs sparse (preview)

| | **Sparse / keyword** (BM25) | **Dense / semantic** (embeddings) |
|---|---|---|
| Looks at | exact **words** | **meaning** |
| "vacation days" finds "annual leave"? | ❌ no shared words | ✅ yes |
| "error E-4021" finds "E-4021"? | ✅ exact match | ⚠️ often weak (rare token) |
| Needs a model? | no | yes (embedding model) |
| Explainable? | yes (which words matched) | not really |
| Speed / cost | very cheap | cheaper than LLM, but needs GPU/API for embeddings |

They fail in **different** places → combine both = **hybrid search**. This is the #1 practical upgrade for a naive RAG.

---

## 6. The three "levels" of RAG

```
 Level 1: NAIVE RAG          Level 2: ADVANCED RAG                 Level 3: AGENTIC RAG
 ─────────────────          ─────────────────────                 ───────────────────
 chunk → embed → top-k      + better chunking                     LLM agent controls the loop:
 → stuff into prompt        + hybrid (BM25 + vectors)             • decides IF to search
                            + re-ranking                          • picks WHICH tool/index
                            + query rewriting                     • rewrites & searches AGAIN
                            + metadata filters                    • checks if docs are relevant
                            + evaluation                          • stops when it has enough
```

Naive RAG works in a demo. Advanced RAG works in production. Agentic RAG handles hard, multi-step questions.

---

## 7. RAG vs fine-tuning vs long context (classic interview question)

| | **RAG** | **Fine-tuning** | **Long context** (paste everything) |
|---|---|---|---|
| Teaches the model… | **facts** (at question time) | **behaviour / style / format** | facts (for this one prompt) |
| Data changes daily? | ✅ just re-index | ❌ re-train every time | ✅ |
| Citations / sources | ✅ easy | ❌ no | ⚠️ possible |
| Access control per user | ✅ filter at search time | ❌ impossible (it's in the weights) | ⚠️ |
| Cost per question | low | low | **high** (you pay for all tokens, every time) |
| Size limit | millions of docs | n/a | context window (and quality drops in the middle) |

**Simple answer for interviews:**
> "RAG for **knowledge**, fine-tuning for **behaviour**. They're not enemies, you can use both:
> fine-tune a model to follow your answer format, and use RAG to give it fresh facts.
> Long context is great for 'analyse these 3 documents now', but too expensive and too noisy for a big knowledge base."

**When NOT to use RAG:**
- The question is about **structured data** ("total sales last month") → use **SQL / text-to-SQL**, not vector search.
- The task needs the **whole document** ("summarise this contract") → give the whole doc (long context or map-reduce).
- The model already knows it (general knowledge) → no retrieval needed (an agent can decide this).

---

## 8. A minimal RAG in 15 lines (so the picture is concrete)

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model

chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)   # INDEXING
store = InMemoryVectorStore.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))

def answer(question: str) -> str:                                                               # QUERY
    hits = store.similarity_search(question, k=4)
    context = "\n\n".join(f"[{i}] ({d.metadata['source']}) {d.page_content}" for i, d in enumerate(hits, 1))
    prompt = f"""Answer ONLY from the context. Cite sources like [1]. If the answer is not there, say "I don't know".
Context:\n{context}\n\nQuestion: {question}"""
    return init_chat_model("gpt-4o-mini", temperature=0).invoke(prompt).content
```

Everything else in this module is about making each of these lines **better**.

---

## Revision notes
- RAG = open-book exam: **retrieve** relevant chunks → **augment** the prompt → **generate** a grounded answer with citations.
- Solves **P-F-H-S-S**: private data, freshness, hallucination, sources, scale.
- Two pipelines: **indexing** (load → clean → chunk → embed → store) and **query** (**T-R-F-R-G**: transform → retrieve → fuse → rerank → generate).
- **Funnel**: cheap search for recall (top 50) → expensive reranker for precision (top 5) → LLM.
- Sparse (BM25, exact words) and dense (embeddings, meaning) fail differently → **hybrid**.
- Levels: naive → advanced → agentic.
- **RAG for knowledge, fine-tuning for behaviour**, long context for "these few docs right now". Structured questions → SQL.

---
✅ **Done with 25.** Next: [26 Ingestion & chunking →](26_ingestion_and_chunking.md)
