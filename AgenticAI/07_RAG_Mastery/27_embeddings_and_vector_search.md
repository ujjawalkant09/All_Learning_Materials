**Part 7 · RAG Mastery** · step 27 of 37
[← 26 Ingestion & chunking](26_ingestion_and_chunking.md) · [🏠 Roadmap](../README.md) · [28 BM25 & Elasticsearch →](28_bm25_and_elasticsearch.md)

# 27 · Embeddings & Vector Search

> **What you'll learn:** what an embedding is, cosine vs dot product vs L2, how to pick an embedding model,
> bi-encoders, why we need *approximate* nearest neighbour search, how **HNSW**, **IVF** and **PQ** work (in
> plain words), vector databases, quantization, and the weak spots of dense retrieval.

---

## 1. Embedding = a "meaning address"

An embedding model turns text into a list of numbers (a **vector**), e.g. 384, 768, 1536 or 3072 numbers.
Think of it as a **GPS address in "meaning space"**: texts with similar meaning live in the same neighbourhood.

```
              ▲  (meaning space, squashed to 2D)
              │     "annual leave policy" ●  ● "how many vacation days"
              │                      ● "paid time off"
              │
              │                                      ● "reset my VPN password"
              │                                    ● "IT login problems"
              └──────────────────────────────────────────────►
```

"Vacation days" and "annual leave" share **zero words** but are neighbours. That's the superpower of dense retrieval.

---

## 2. Measuring "closeness"

| Metric | Formula idea | Notes |
|---|---|---|
| **Cosine similarity** | angle between two vectors (−1..1) | ignores length; the default for text |
| **Dot product** | `a · b` | = cosine if vectors are normalised (length 1). Fastest |
| **Euclidean (L2) distance** | straight-line distance | for normalised vectors, ranks the same as cosine |

**Practical rule:** normalise your vectors and use dot product / cosine. Use the metric the model was trained with (check its model card).

```python
import numpy as np
def cosine(a, b): return a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## 3. Bi-encoder: how an embedding model is used in search

```
 Query ──► [ Encoder ] ──► q vector ─┐
                                     ├──► cosine(q, d) = score
 Doc   ──► [ Encoder ] ──► d vector ─┘
```

- Query and document are encoded **separately** ("bi" = two sides).
- So we can embed **all documents once, offline**, and at query time embed only the query. That's what makes it fast.
- Downside: the query and document never "see" each other inside the model → less accurate than a **cross-encoder** (step 29).

Training idea (contrastive learning): pull (question, correct passage) pairs together, push random passages away.

---

## 4. Choosing an embedding model

| Question | Guidance |
|---|---|
| Where to compare? | **MTEB leaderboard** (retrieval tab), but test on **your** data, leaderboards don't know your domain |
| Hosted or local? | Hosted (OpenAI `text-embedding-3-small/large`, Cohere, Voyage, Google): easy. Local (`bge`, `e5`, `gte`, `nomic`, `all-MiniLM-L6-v2` for learning): private + no per-call cost |
| Dimensions? | More dims = more detail but more RAM/disk. 384–1024 is often enough. **Matryoshka** models let you cut vectors (e.g. 3072 → 256) with small quality loss |
| Max input length? | Must be ≥ your chunk size, or text gets silently truncated! |
| Languages? | Multilingual model if users ask in Hindi and docs are in English |
| Asymmetric prefixes? | Some models (e5, bge, nomic) need prefixes like `"query: "` / `"passage: "`. Forgetting them lowers quality |
| Domain? | Legal/medical/code have special models; or **fine-tune** an embedding model on your (question, passage) pairs |

**Golden rule:** use the **same model** for documents and queries. Changing model = re-embed everything.

---

## 5. Why not just compare the query with every vector? (exact vs approximate search)

**Exact (brute force / "flat") search:** compute similarity with all N vectors.
- 10k vectors → fine (milliseconds). Use it! (FAISS `IndexFlatIP`)
- 100M vectors × 1024 dims → too slow for every query.

**ANN = Approximate Nearest Neighbour:** find *almost* the best neighbours, **much** faster.
We trade a tiny bit of **recall** (maybe we miss 1–5% of true neighbours) for 100–1000× speed.

### 5.1 HNSW (Hierarchical Navigable Small World) ✅ most common

**Analogy: travelling with highways, then city roads, then streets.**

```
 Layer 2 (few nodes, long jumps)     A ─────────────────────── B            ← highway
 Layer 1 (more nodes)                A ──── C ──────── D ───── B            ← main roads
 Layer 0 (all nodes, short links)    A─E─C─F─G─D─H─I─B─J─K ...              ← streets
```
- Start at the top layer, greedily jump to the node closest to the query.
- Go down a layer, continue greedily, and so on until layer 0.
- Each node only connects to a few neighbours, so you look at a tiny part of the data.

Knobs (interview favourites):
| Param | Meaning | Bigger value → |
|---|---|---|
| `M` | links per node | better recall, more memory |
| `ef_construction` | how hard we search while building | better graph, slower build |
| `ef_search` (or `num_candidates` in Elasticsearch) | how many candidates we keep while searching | **better recall, slower query** |

Pros: fast, high recall, supports adding vectors. Cons: uses a lot of RAM; deletes are awkward.

### 5.2 IVF (Inverted File index)
**Analogy: a library with sections.** Cluster all vectors into, say, 1,000 groups (k-means). At query time, find the
`nprobe` closest group centres and only search inside those groups.
- `nlist` = number of clusters, `nprobe` = how many clusters to check. Bigger `nprobe` = better recall, slower.

### 5.3 PQ (Product Quantization) = compression
**Analogy: describing a face as "eyes type 12, nose type 3, mouth type 40"** instead of a full photo.
Split each vector into chunks, replace each chunk with the id of its nearest "prototype". 1024 floats (4 KB) → ~64 bytes.
Huge memory savings, some accuracy loss. Often combined: **IVF-PQ**.

### 5.4 Quantization (scalar/binary)
- **float32 → int8**: 4× smaller, tiny quality loss.
- **binary** (1 bit per dim): 32× smaller, use it for a fast first pass, then **rescore** the top candidates with full vectors.

### 5.5 DiskANN / ScaNN
Graph indexes that live mostly **on SSD** (DiskANN) or Google's optimised ANN (ScaNN). Know the names: for billions of vectors.

---

## 6. Vector databases: what to pick

| Option | Type | Pick when |
|---|---|---|
| **FAISS** | library (no server) | local, fast, research, you manage files yourself |
| **Chroma** | simple DB (embedded or server) | prototypes, small apps |
| **pgvector** (Postgres) | extension | you already use Postgres; want SQL joins + vectors + ACID |
| **Elasticsearch / OpenSearch** | search engine | you need **BM25 + vectors + filters + aggregations** in one place, big scale |
| **Qdrant / Weaviate / Milvus** | dedicated vector DBs | big vector workloads, good filtering, hybrid support |
| **Pinecone** | managed SaaS | no ops, pay per use |
| **Typesense** | search engine | simple hybrid search, typo tolerance (installed in this repo) |

What actually matters when choosing: **filtering** support (pre-filter vs post-filter), **hybrid** search, scale & cost, ops burden, multi-tenancy, and whether you already run something (Postgres/ES).

### Pre-filter vs post-filter (common trap)
- **Post-filter:** get top 10 by vector, *then* drop the ones that fail the filter → you might end with 0 results!
- **Pre-filter / filtered search:** apply the filter *during* the ANN search → correct k results. Prefer DBs that do this.

---

## 7. Weak spots of dense retrieval (know these cold)

| Weakness | Example | Fix |
|---|---|---|
| Exact tokens: IDs, codes, names, rare words | "error E-4021", "SKU 88-1032", "Kubernetes 1.31" | **Hybrid with BM25** |
| Negation | "flights **not** via Dubai" ≈ "flights via Dubai" | rerank / LLM filtering |
| Numbers and dates | "2023 policy" vs "2026 policy" look the same | metadata filters (`year=2026`) |
| Out-of-domain jargon | internal acronyms the model never saw | BM25, glossary/synonym expansion, fine-tune embedder |
| Long docs in one vector | meaning averaged away | better chunking |
| Query ≠ doc style | short question vs long formal answer | HyDE, hypothetical-question indexing (step 30, 26) |
| Similar ≠ relevant | "how to cancel" retrieves "how to subscribe" | **cross-encoder reranking** |

---

## 8. Code: dense search with a local model + FAISS

```python
from sentence_transformers import SentenceTransformer
import faiss, numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")      # 384 dims, runs on CPU
doc_vecs = model.encode(texts, normalize_embeddings=True).astype("float32")

index = faiss.IndexFlatIP(doc_vecs.shape[1])     # exact search, inner product (= cosine because normalised)
# index = faiss.IndexHNSWFlat(384, 32)           # ANN with HNSW, M=32 (uses L2; same ranking for normalised vecs)
index.add(doc_vecs)

q = model.encode(["how many vacation days?"], normalize_embeddings=True).astype("float32")
scores, ids = index.search(q, 5)
```
Runnable version: [36 Lab: hybrid + rerank pipeline](36_lab_hybrid_rerank_pipeline.ipynb).

---

## Revision notes
- Embedding = **meaning address**; similar meaning → nearby vectors. Cosine (or dot product on normalised vectors).
- **Bi-encoder**: query and docs encoded separately → docs embedded once offline → fast, but less accurate than a cross-encoder.
- Pick models via MTEB **and your own eval**; check max length, dims, language, prefixes. Same model for query and docs.
- Exact search for small data; **ANN** for big data: **HNSW** (highway graph; `M`, `ef_construction`, `ef_search`), **IVF** (clusters; `nlist`, `nprobe`), **PQ** (compression).
- Bigger `ef_search`/`nprobe`/`num_candidates` = better recall, slower.
- Prefer **pre-filtering**; post-filtering can return zero results.
- Dense is weak on **exact tokens, negation, numbers, jargon** → hybrid + reranker + metadata filters.

---
✅ **Done with 27.** Next: [28 BM25 & Elasticsearch →](28_bm25_and_elasticsearch.md)
