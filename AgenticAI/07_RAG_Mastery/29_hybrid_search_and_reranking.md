**Part 7 · RAG Mastery** · step 29 of 37
[← 28 BM25 & Elasticsearch](28_bm25_and_elasticsearch.md) · [🏠 Roadmap](../README.md) · [30 Query transformation & routing →](30_query_transformation_and_routing.md)

# 29 · Hybrid Search, RRF & Re-ranking (Cross-Encoders)

> **What you'll learn:** why combine keyword + vector search, how to fuse two ranked lists (score
> normalisation vs **Reciprocal Rank Fusion**), the difference between **bi-encoder**, **cross-encoder** and
> **ColBERT**, LLM rerankers, MMR for diversity, and how to order chunks in the prompt.

---

## 1. Hybrid search: two detectives are better than one

```
                       ┌──► BM25 (keyword detective: "finds the exact words") ──► ranked list A ─┐
 query ────────────────┤                                                                          ├──► FUSE ──► one list
                       └──► Dense (meaning detective: "finds the same idea")  ──► ranked list B ─┘
```

| Query | BM25 alone | Dense alone | Hybrid |
|---|---|---|---|
| "error E-4021 on checkout" | ✅ exact code | ❌ finds generic checkout errors | ✅ |
| "how many vacation days do I get" | ❌ docs say "annual leave" | ✅ | ✅ |
| "NimbusDB free tier limits" | ✅ product name | ✅ | ✅✅ (agreement = more confidence) |

Hybrid is almost never worse than either alone, and usually clearly better. **It's the default for production RAG.**

---

## 2. How to fuse two lists

### Problem: the scores are on different scales
BM25 scores: 0 to 25+, unbounded, depend on the query. Cosine scores: about 0.2 to 0.9. Adding them directly is meaningless.

### Option A: score normalisation + weighted sum ("convex combination")
```
final = α × norm(dense_score) + (1 − α) × norm(bm25_score)        e.g. α = 0.5–0.7
norm  = min-max scaling to 0..1 within this query's results
```
Works well **if** you tune α on an eval set. Sensitive to outliers (one huge BM25 score squashes the others).

### Option B: Reciprocal Rank Fusion (RRF) ✅ simple, robust, no tuning
**Ignore the scores, use only the ranks.**

```
 RRF_score(doc) =   Σ    1 / (k + rank_in_list)            k = 60 (standard constant)
                 over lists
```

**Worked example** (k = 60):

| Doc | BM25 rank | Dense rank | RRF score |
|---|---|---|---|
| A | 1 | 4 | 1/61 + 1/64 = 0.01639 + 0.01563 = **0.03202** 🥇 |
| B | 2 | — (not found) | 1/62 = **0.01613** |
| C | — | 1 | 1/61 = **0.01639** |
| D | 3 | 2 | 1/63 + 1/62 = 0.01587 + 0.01613 = **0.03200** 🥈 |

A and D appear in **both** lists → they win. A document found by only one retriever can still rank, but
agreement is rewarded. **Memory hook: "RRF rewards agreement."**

Why `k = 60`? It flattens the curve so that rank 1 vs rank 2 isn't a huge jump; it stops a single list from
dominating. You rarely need to change it. You *can* weight lists: `w_bm25/(k+r1) + w_dense/(k+r2)`.

```python
def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```
LangChain: `EnsembleRetriever(retrievers=[bm25, dense], weights=[0.5, 0.5])` uses weighted RRF.

---

## 3. Re-ranking: the careful second reader

First-stage retrieval (BM25/dense) is built for **speed** over millions of docs. It's good at getting the right
answer **into the top 50**, but not at putting it **at #1**. A re-ranker reads each (query, candidate) pair
carefully and re-orders them.

### Bi-encoder vs cross-encoder: the key interview diagram

```
 BI-ENCODER (retrieval)                         CROSS-ENCODER (re-ranking)
 ─────────────────────                          ──────────────────────────
  query ──► [Encoder] ──► vec q ─┐               "[CLS] query [SEP] document [SEP]"
                                 ├─► cosine                    │
  doc   ──► [Encoder] ──► vec d ─┘                     [ ONE Transformer ]   ← every query word attends
                                                               │               to every doc word
  docs encoded ONCE, offline ✅                                ▼
  query & doc never "see" each other ❌                  relevance score (e.g. 0.93)
                                                    must run for EVERY pair at query time ❌
                                                    much more accurate ✅
```

**Analogy:**
- Bi-encoder = HR filters 10,000 CVs by **keywords on a summary card**. Fast, rough.
- Cross-encoder = a **hiring manager reads** the top 50 CVs **next to the job description**. Slow, precise.

| | Bi-encoder | Cross-encoder |
|---|---|---|
| Input | query and doc separately | query + doc **together** |
| Precompute docs? | ✅ yes | ❌ no |
| Speed for 1M docs | ms (with ANN) | impossible (1M model calls) |
| Speed for 50 docs | — | ~50–300 ms on CPU/GPU |
| Accuracy | good | **better** |
| Use for | **retrieval** (stage 1) | **re-ranking** (stage 2) |

### Code (local, free, runs on CPU)
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
pairs = [(query, doc.page_content) for doc in candidates]           # candidates = top 30–50 from hybrid
scores = reranker.predict(pairs)
top5 = [d for _, d in sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)][:5]
```
Other rerankers: `BAAI/bge-reranker-v2-m3` (multilingual), **Cohere Rerank**, **Voyage rerank**, **Jina reranker**, Elastic's rerank.

### How many to rerank?
- Retrieve **20–100**, rerank, keep **3–10** for the LLM.
- More candidates = higher chance the right one is there (recall), but more latency. Measure both.
- Use the reranker score as a **threshold** too: if the best score is very low → "I don't know" instead of a wrong answer.

---

## 4. ColBERT: the middle ground (late interaction)

ColBERT keeps **one vector per token** (not one per document). Score = for each query token, find its best-matching
doc token (MaxSim), then sum.
- Docs can be pre-encoded (like a bi-encoder) ✅
- Token-level matching gives near cross-encoder quality ✅
- Storage is big (a vector per token) ❌ → compression in ColBERTv2 / PLAID.
- Tools: RAGatouille, Vespa, some vector DBs support "multi-vector".

```
 Bi-encoder:  1 vec vs 1 vec         (fast, coarse)
 ColBERT:     many vecs vs many vecs  (fast-ish, fine)    ← "late interaction"
 Cross-enc:   full attention          (slow, finest)      ← "early/full interaction"
```

---

## 5. LLM as a reranker

Ask an LLM to score or order passages.
- **Pointwise:** "Rate 0–10 how relevant this passage is to the question." (simple, parallel, scores are noisy)
- **Pairwise:** "Which of A or B is more relevant?" (accurate, many calls)
- **Listwise:** "Here are 20 passages, return their ids in order of relevance." (RankGPT style; position bias, use a sliding window)

Pros: smart, understands instructions ("prefer the newest policy"). Cons: slow and expensive. Often: cross-encoder first, LLM filter on the final few.

---

## 6. Diversity: MMR (Maximal Marginal Relevance)

Top-5 can be 5 near-copies of the same paragraph (overlap, duplicate docs). MMR picks the next doc that is
**relevant to the query** but **different from what's already picked**:

```
 MMR = λ × sim(query, doc)  −  (1 − λ) × max sim(doc, already_selected)        λ ≈ 0.5–0.7
```
Use when questions need several aspects ("compare plan A and plan B"). LangChain: `search_type="mmr"`.

---

## 7. Ordering chunks in the prompt ("lost in the middle")

LLMs pay most attention to the **start and end** of a long context and less to the middle.
- Send **fewer, better** chunks (reranking helps more than stuffing 30 chunks).
- Put the most relevant chunks **first** (and optionally the 2nd best **last**). LangChain: `LongContextReorder`.
- Label chunks with ids and sources: `[1] (hr/leave.pdf p.3) ...` so the model can cite.

---

## 8. The full retrieval stack (what a strong production system looks like)

```
 query
   │  (optional) rewrite / expand                                    [30]
   ▼
 ┌─────────────── first stage: RECALL, top ~50 each ───────────────┐
 │  BM25 (with filters)          Dense kNN (with same filters)     │
 └───────────────────────┬─────────────────────────────────────────┘
                         ▼
                  RRF fusion → top 50
                         ▼
          Cross-encoder rerank → top 5–8   (drop if score < threshold)
                         ▼
          (optional) MMR / dedupe → expand to parent chunks
                         ▼
          prompt with numbered, cited chunks → LLM
```
Runnable: [36 Lab: hybrid + rerank pipeline](36_lab_hybrid_rerank_pipeline.ipynb). It measures each stage so you
can **see** recall and MRR go up.

---

## Revision notes
- **Hybrid = BM25 (exact words) + dense (meaning)**; they fail differently, together they're robust.
- Scores aren't comparable → normalise + weight (needs tuning) or **RRF: Σ 1/(60 + rank)** (no tuning). **RRF rewards agreement.**
- **Bi-encoder** = separate encoding, precomputed, fast → retrieval. **Cross-encoder** = query+doc together, accurate, slow → rerank top 20–100.
- Analogy: CV keyword filter (bi) vs hiring manager reading CVs (cross).
- **ColBERT** = token-level late interaction, between the two.
- LLM rerankers: pointwise / pairwise / listwise; powerful, expensive.
- **MMR** for diversity. **Lost in the middle**: fewer chunks, best first, cite with ids.
- Reranker score threshold → safe "I don't know".

---
✅ **Done with 29.** Next: [30 Query transformation & routing →](30_query_transformation_and_routing.md)
