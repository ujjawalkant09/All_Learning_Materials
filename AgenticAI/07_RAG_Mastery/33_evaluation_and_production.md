**Part 7 · RAG Mastery** · step 33 of 37
[← 32 Agentic RAG & agentic search](32_agentic_rag_and_agentic_search.md) · [🏠 Roadmap](../README.md) · [34 Interview questions →](34_interview_questions.md)

# 33 · Evaluation & Production RAG

> **What you'll learn:** how to measure retrieval (**Recall@k, Precision@k, MRR, nDCG, Hit rate**) and
> generation (**faithfulness, answer relevance, context precision/recall, correctness**), how to build an
> eval set, LLM-as-judge, RAGAS, and everything for production: latency, cost, caching, security, monitoring,
> scaling and updates.

**Golden rule: "If you can't measure it, you can't improve it."** Every change (chunk size, model, reranker)
should be judged by numbers on the same test set, not by "it feels better".

---

## 1. Two things to evaluate, separately

```
 question ──► [ RETRIEVER ] ──► chunks ──► [ GENERATOR ] ──► answer
                    │                            │
          Retrieval metrics:              Generation metrics:
          did we FIND the right chunks?   did we USE them well?
          Recall@k, MRR, nDCG             Faithfulness, relevance, correctness
```
If retrieval recall is low, fix retrieval first: the generator can't use what it never saw.

---

## 2. Retrieval metrics (with a tiny example)

Query: "How many leave days?" Relevant chunks: **{A, B}**. Retriever returns: `[C, A, D, B, E]`.

| Metric | Question it answers | Calculation here |
|---|---|---|
| **Hit rate@k** | is at least one relevant in top-k? | @1: C ❌ → 0; @3: A ✅ → **1** |
| **Recall@k** | what fraction of relevant chunks are in top-k? | @3: {A} of {A,B} = **0.5**; @5: **1.0** |
| **Precision@k** | what fraction of top-k is relevant? | @5: 2/5 = **0.4** |
| **MRR** (Mean Reciprocal Rank) | how high is the **first** relevant one? | first relevant at rank 2 → 1/2 = **0.5** (averaged over queries) |
| **nDCG@k** | are relevant ones near the **top** (graded relevance ok)? | gains discounted by `1/log2(rank+1)`, divided by the ideal ordering |

nDCG@5 for this example: DCG = 1/log2(3) + 1/log2(5) = 0.631 + 0.431 = 1.062; ideal (A,B at ranks 1–2) = 1 + 0.631 = 1.631 → **nDCG = 0.651**.

Which to use:
- **Recall@50** for the first stage (is it in the candidate pool for the reranker?).
- **MRR / nDCG@5 / Recall@5** for the final list sent to the LLM.
- Memory hook: **"Recall = did we find it? MRR = how fast? nDCG = in a good order?"**

All metrics are implemented from scratch in [35 Lab](35_lab_search_from_scratch.ipynb).

---

## 3. Generation metrics (the "RAG triad" + correctness)

| Metric | Question | Needs |
|---|---|---|
| **Faithfulness / groundedness** | is every claim in the answer supported by the retrieved context? (= no hallucination) | question, context, answer |
| **Answer relevance** | does the answer actually address the question? | question, answer |
| **Context relevance / precision** | are the retrieved chunks relevant (how much noise)? | question, context |
| **Context recall** | does the context contain everything needed for the reference answer? | context, reference answer |
| **Answer correctness** | does it match the reference (ground-truth) answer? | answer, reference |
| **Citation accuracy** | do the cited sources really support each claim? | answer, citations, context |

**The RAG triad** (TruLens): context relevance → groundedness → answer relevance. If all three are high, the answer is very likely good.

### How these are scored: LLM-as-judge
A strong LLM grades with a rubric, e.g. faithfulness: "Split the answer into claims. For each claim, is it
supported by the context? Score = supported / total."
Tips:
- Use **structured output** (`{"score": int, "reason": str}`), binary or small scales (0–3) are more reliable than 1–10.
- **Calibrate** the judge against ~50 human-labelled examples before trusting it.
- Watch for biases: position bias, verbosity bias, self-preference (judge likes its own model's style).

### Tools
- **RAGAS** (faithfulness, answer relevancy, context precision/recall, etc.)
- **DeepEval**, **TruLens**, **LangSmith evaluators**, **Arize Phoenix**, **promptfoo**.
They're all implementations of the same ideas above. Know the ideas, the tool is a detail.

---

## 4. Building an evaluation set (the real work)

1. **Collect real questions** (support tickets, search logs, ask users). 50–200 to start.
2. For each: the **expected source chunk(s)** (for retrieval metrics) and a **reference answer** (for correctness).
3. Include **hard cases**: multi-hop, exact IDs, follow-ups, numbers/tables, "not in the docs" (must refuse), ambiguous, other languages, ACL cases (user must NOT see this).
4. **Synthetic data** to scale: an LLM reads a chunk and writes questions it answers (RAGAS/LLM generation). Review a sample by hand: synthetic questions are often too easy (they copy the chunk's words).
5. Version the set; add every production failure to it (**regression tests**).
6. Run it in **CI** on every change; compare with the last baseline.

### Experiment table (how to tune with evidence)
| Config | Recall@50 | MRR@5 | Faithfulness | p95 latency | $ / 1k q |
|---|---|---|---|---|---|
| dense only, chunk 500 | 0.78 | 0.52 | 0.86 | 1.9 s | 1.10 |
| + BM25 (RRF) | 0.89 | 0.58 | 0.88 | 2.0 s | 1.10 |
| + cross-encoder rerank | 0.89 | 0.74 | 0.92 | 2.3 s | 1.15 |
| + contextual chunks | 0.94 | 0.79 | 0.93 | 2.3 s | 1.20 |
(Illustrative numbers. The point is the **format**: change one thing at a time, measure quality, latency and cost together.)

---

## 5. Production concerns

### 5.1 Latency budget (typical)
```
 query rewrite (small LLM)      150–400 ms   ← skip when not needed
 embedding the query             10–50 ms
 BM25 + ANN (parallel)           10–50 ms
 rerank 50 docs                 50–300 ms
 LLM generation                 1–5 s        ← stream tokens so the user sees progress immediately
```
Speed-ups: **stream**, run retrievers **in parallel**, smaller reranker / fewer candidates, cache, smaller model for
side tasks (rewrite, grading), keep the prompt short.

### 5.2 Caching
- **Embedding cache**: never embed the same text twice (hash → vector).
- **Retrieval/answer cache**: exact same question → stored answer (invalidate when docs change).
- **Semantic cache**: very similar question (cosine > 0.95) → reuse answer. Careful: "leave days for interns" vs "for employees" are similar but different answers! Use a high threshold and scope by user/tenant.
- **Prompt caching** (provider feature): a long, fixed system prompt is charged less on repeat.

### 5.3 Cost levers
Fewer/shorter chunks, cheaper models for rewriting/grading, skip retrieval for small talk, batch embeddings
at ingestion, smaller embedding dims (Matryoshka), quantized vectors.

### 5.4 Security & privacy (asked often!)
- **Access control at retrieval time:** every chunk carries `allowed_groups`/`tenant_id`; the search **filter** uses the logged-in user's groups from a trusted source. Never rely on the LLM to hide data.
- **Multi-tenancy:** separate index per tenant, or a mandatory `tenant_id` filter enforced in code.
- **Prompt injection** in documents/web pages: treat retrieved content as data, delimit it, restrict tool permissions, human approval for actions, filter outputs (e.g. no secrets, no unexpected URLs).
- **PII:** redact at ingestion or at output; audit logs.
- **Data poisoning:** only index trusted sources; track provenance.

### 5.5 Monitoring & feedback (after launch)
Log for every request: question, rewritten query, retrieved ids + scores, reranker scores, final prompt size,
answer, latency per stage, tokens, user feedback.
Watch: 👍/👎 rate, "I don't know" rate, low-reranker-score rate, latency p95, cost per day, top unanswered
questions (→ content gaps). Sample and review conversations weekly.

### 5.6 Scaling
- Millions of chunks: ANN (HNSW) + quantization; shard the index (Elasticsearch/OpenSearch/Milvus/Qdrant clusters).
- Ingestion: queue + workers, batch embeddings, incremental updates (hash), idempotent upserts.
- Zero-downtime changes: build new index → validate on eval set → swap alias.

### 5.7 Production checklist ✅
- [ ] Clean parsing, metadata (`doc_id`, source, dates, ACL), dedupe
- [ ] Hybrid search + reranker + threshold for abstaining
- [ ] Grounded prompt with citations; structured output where needed
- [ ] ACL & tenant filters enforced in code
- [ ] Eval set + retrieval & generation metrics in CI
- [ ] Tracing/logging per stage; dashboards; feedback buttons
- [ ] Incremental sync, deletes, re-index plan for model changes
- [ ] Caching, streaming, timeouts, retries, fallbacks (if reranker is down → use fused list)
- [ ] Prompt-injection defences; PII handling

---

## Revision notes
- Evaluate **retrieval** and **generation** separately; fix retrieval first.
- Retrieval: **Hit@k, Recall@k, Precision@k, MRR, nDCG**. Hook: *Recall = found? MRR = how fast? nDCG = good order?*
- Generation: **faithfulness**, **answer relevance**, **context precision/recall**, **correctness**, citation accuracy. **RAG triad** = context relevance → groundedness → answer relevance.
- LLM-as-judge: rubric, small scales, structured output, calibrate on human labels, watch biases. Tools: RAGAS, DeepEval, TruLens, LangSmith.
- Eval set: real questions + hard cases (refusal, multi-hop, IDs, ACL) + reviewed synthetic data; run in CI; add every failure.
- Production: latency budget + streaming, caching (embedding/answer/**semantic** with care), cost levers, **ACL at retrieval**, prompt injection, monitoring, alias-swap re-index.

---
✅ **Done with 33.** Next: [34 Interview questions →](34_interview_questions.md)
