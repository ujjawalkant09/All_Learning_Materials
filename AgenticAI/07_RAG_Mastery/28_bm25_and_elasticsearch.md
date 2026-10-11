**Part 7 · RAG Mastery** · step 28 of 37
[← 27 Embeddings & vector search](27_embeddings_and_vector_search.md) · [🏠 Roadmap](../README.md) · [29 Hybrid search & reranking →](29_hybrid_search_and_reranking.md)

# 28 · Keyword Search: Inverted Index, TF-IDF, BM25 & Elasticsearch

> **What you'll learn:** how keyword search really works (inverted index, analyzers), TF-IDF, the **BM25**
> formula explained piece by piece with a worked example, `k1` and `b`, then **Elasticsearch**: index,
> shards, replicas, mappings, analyzers, query DSL, `dense_vector` + kNN, and hybrid search with RRF.
> Plus learned sparse retrieval (SPLADE / ELSER).

---

## 1. Why keyword search still matters in the age of embeddings

Users search for **exact things**: an error code `E-4021`, a person "Priya Sharma", a product "NimbusDB",
a clause number "Section 7.2(b)". Embeddings blur these. Keyword search nails them.
It is also **cheap, fast, explainable, and needs no model**. Every serious RAG system uses it in hybrid.

---

## 2. The inverted index (the heart of every search engine)

**Analogy: the index at the back of a textbook.** Instead of reading every page to find "photosynthesis",
you look up the word and it tells you "pages 12, 45, 88".

```
 Documents                                   Inverted index (term → postings list)
 D1: "Reset VPN password"                    reset    → [D1]
 D2: "VPN setup guide for VPN client"        vpn      → [D1 (tf=1), D2 (tf=2)]
 D3: "Annual leave policy"                   password → [D1]
                                             setup    → [D2]
                                             leave    → [D3] ...
```

To answer a query, the engine only reads the postings lists of the query words: super fast even for billions of docs.

### Analyzers: how text becomes terms
Both documents (at index time) and queries (at search time) go through the **same analyzer**:

```
"Resetting the VPN-Passwords!"
   │ character filters   (strip HTML, map characters)
   ▼
   │ tokenizer           → ["Resetting", "the", "VPN", "Passwords"]
   ▼
   │ token filters       lowercase → ["resetting","the","vpn","passwords"]
   │                     stop words → ["resetting","vpn","passwords"]
   │                     stemming   → ["reset","vpn","password"]
   ▼
 terms stored in the index
```
- **Stemming** (`running` → `run`) and **synonyms** (`pto` ↔ `vacation` ↔ `annual leave`) give keyword search a bit of "meaning".
- If index-time and query-time analysis differ, matches silently fail. Classic bug.

---

## 3. TF-IDF: the intuition BM25 builds on

A word is important for a document if:
- **TF (term frequency):** it appears **often in this doc**, and
- **IDF (inverse document frequency):** it is **rare across all docs**.

"the" appears everywhere → IDF ≈ 0 → useless. "kubernetes" appears in 3 of 10,000 docs → high IDF → very informative.

Problem with plain TF-IDF: TF grows **without limit** (a doc that says "vpn" 50 times is not 50× more relevant), and long docs win just by being long. BM25 fixes both.

---

## 4. BM25 (Best Match 25), explained piece by piece

```
                         Σ   IDF(t)  ×        tf(t,D) × (k1 + 1)
 score(D, Q)  =      t in Q          ─────────────────────────────────────────────
                                      tf(t,D) + k1 × (1 − b + b × |D| / avgdl)

 IDF(t) = ln( 1 + (N − n(t) + 0.5) / (n(t) + 0.5) )        ← Lucene / Elasticsearch version
```

| Symbol | Meaning |
|---|---|
| `t` | a query term |
| `tf(t,D)` | how many times `t` appears in document D |
| `N` | total number of documents |
| `n(t)` | number of documents containing `t` |
| `|D|` | length of D (in terms), `avgdl` = average doc length |
| `k1` | **TF saturation** (default **1.2**). How fast extra repeats stop helping |
| `b` | **length normalisation** (default **0.75**). 0 = ignore length, 1 = fully normalise |

### The three ideas to remember: **"Rare, Repeated (but saturating), Short"**
1. **Rare words matter more** → IDF.
2. **Repeating a word helps, but with diminishing returns** → saturation via `k1`.
   With k1 = 1.2, the TF part goes 1 → 1.0, 2 → 1.38, 3 → 1.57, … and never exceeds `k1 + 1 = 2.2`.
3. **A match in a short doc counts more than in a long doc** → length normalisation via `b`.

```
 TF part
 2.2 ┤· · · · · · · · · · · · · · · · · · · · · ·  ← ceiling = k1 + 1
     │                 ●───────●──────●────●
 1.5 ┤         ●────●
     │    ●
 1.0 ┤●
     └┬────┬────┬────┬────┬────┬────► tf
      1    2    3    4    5    6        TF-IDF would be a straight line going up forever
```

### Worked example (numbers computed exactly, also in the lab notebook)

Docs (after analysis): `D1 = "reset vpn password"` (3 terms), `D2 = "vpn setup guide for vpn client on mac"` (8),
`D3 = "annual leave policy and leave carry over"` (7). `N = 3`, `avgdl = 6`, `k1 = 1.2`, `b = 0.75`.
Query: **"vpn password"**.

| Term | n(t) | IDF |
|---|---|---|
| vpn | 2 | ln(1 + 1.5/2.5) = **0.470** |
| password | 1 | ln(1 + 2.5/1.5) = **0.981** (rarer → bigger) |

| Doc | vpn part | password part | **BM25** |
|---|---|---|---|
| D1 (short, vpn×1, password×1) | 0.591 | 1.233 | **1.824** 🥇 |
| D2 (long, vpn×2) | 0.591 | 0 | **0.591** |
| D3 | 0 | 0 | 0 |

Look at the "vpn" column: D2 says "vpn" **twice** but gets the **same** score as D1 saying it once, because
D2 is long (length normalisation) and repeats saturate. And the rare word "password" decides the winner.

### Tuning k1 and b
- Short texts (titles, tweets): lower `b` (length matters less).
- Long, repetitive docs: lower `k1` (repeats matter less).
- Defaults (1.2 / 0.75) are good. Tune only with an evaluation set.

### BM25 weaknesses
- **Vocabulary mismatch:** "vacation" doesn't match "annual leave" (fix: synonyms, hybrid with dense, query expansion).
- No understanding of word order or meaning ("dog bites man" = "man bites dog").
- Typos (fix: `fuzziness` in Elasticsearch).

Python quick start (no server): `pip install rank_bm25` → `BM25Okapi(tokenized_docs).get_scores(query_tokens)`.
Our lab writes it **from scratch**: [35 Lab](35_lab_search_from_scratch.ipynb).

---

## 5. Elasticsearch in plain words

**Elasticsearch (ES)** = a distributed search engine built on **Apache Lucene**. You send JSON documents over
HTTP; it builds inverted indexes (BM25) and vector indexes (HNSW) and searches them fast. **OpenSearch** is the
open-source fork (AWS). Concepts are almost the same.

### Core vocabulary

| ES term | Database analogy | Meaning |
|---|---|---|
| **Index** | table | a collection of documents (e.g. `company-docs`) |
| **Document** | row | one JSON object (one chunk, for RAG) |
| **Field** | column | `content`, `title`, `department`, `embedding` |
| **Mapping** | schema | field types: `text` (analyzed, BM25), `keyword` (exact, for filters), `date`, `dense_vector` |
| **Shard** | partition | an index is split into shards spread over nodes → scale |
| **Replica** | backup copy | copy of a shard → high availability + more read throughput |
| **Node / cluster** | server / group of servers | |
| **Segment** | | immutable Lucene file inside a shard; new docs → new segments, merged in background |
| **Refresh** | | makes new docs searchable (default ~1 s → "near real-time") |

```
 Cluster
 ├── Node 1: [shard 0 primary] [shard 1 replica]
 ├── Node 2: [shard 1 primary] [shard 2 replica]
 └── Node 3: [shard 2 primary] [shard 0 replica]
 Query → coordinating node → asks every shard → each returns its top-k → merge → final top-k
```

### `text` vs `keyword` (most common beginner mistake)
- `text`: analyzed into terms, scored with BM25 → for **searching** content.
- `keyword`: stored as one exact value → for **filters, sorting, aggregations** (`department: "HR"`).
- Use both on one field with a multi-field: `"title": {"type": "text", "fields": {"raw": {"type": "keyword"}}}`.

### Query vs filter context
- **Query context** (`must`, `should`): "how well does it match?" → affects the score.
- **Filter context** (`filter`, `must_not`): "yes or no?" → no scoring, **cached**, faster. Put access control and metadata here.

---

## 6. Elasticsearch for RAG: a full example

Run locally (single node, security off, only for learning):
```bash
docker run -d --name es -p 9200:9200 -e discovery.type=single-node -e xpack.security.enabled=false \
  -e ES_JAVA_OPTS="-Xms1g -Xmx1g" docker.elastic.co/elasticsearch/elasticsearch:8.15.0
uv add elasticsearch      # python client
```
Runnable script: [elasticsearch_lab/es_hybrid_demo.py](elasticsearch_lab/es_hybrid_demo.py).

### 6.1 Mapping: BM25 field + vector field + filter fields
```json
PUT company-docs
{
  "settings": {
    "analysis": {
      "filter":   { "my_synonyms": { "type": "synonym_graph", "synonyms": ["pto, vacation, annual leave"] } },
      "analyzer": { "en_syn": { "tokenizer": "standard", "filter": ["lowercase", "my_synonyms", "porter_stem"] } }
    }
  },
  "mappings": {
    "properties": {
      "content":        { "type": "text", "analyzer": "standard", "search_analyzer": "en_syn" },
      "title":          { "type": "text" },
      "department":     { "type": "keyword" },
      "allowed_groups": { "type": "keyword" },
      "updated_at":     { "type": "date" },
      "embedding":      { "type": "dense_vector", "dims": 384, "index": true, "similarity": "cosine" }
    }
  }
}
```
(`synonym_graph` belongs in the **search** analyzer; that's why it is only in `search_analyzer`.)

### 6.2 BM25 search with filters and field boosting
```json
GET company-docs/_search
{
  "query": {
    "bool": {
      "must":   [{ "multi_match": { "query": "vpn password reset", "fields": ["title^2", "content"] } }],
      "filter": [{ "terms": { "allowed_groups": ["all_employees", "engineering"] } },
                 { "range": { "updated_at": { "gte": "2025-01-01" } } }]
    }
  }
}
```
`title^2` = a match in the title counts double.

### 6.3 Vector (kNN) search
```json
GET company-docs/_search
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.12, -0.03, ...],
    "k": 10,
    "num_candidates": 100,
    "filter": { "terms": { "allowed_groups": ["all_employees"] } }
  }
}
```
`num_candidates` = how many candidates HNSW looks at per shard (like `ef_search`): higher = better recall, slower.
The `filter` here is a **pre-filter** (applied during the vector search), so you still get k results.

### 6.4 Hybrid search: BM25 + kNN fused with RRF
Newer ES versions (8.14+) have **retrievers**:
```json
GET company-docs/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        { "standard": { "query": { "match": { "content": "vpn password reset" } } } },
        { "knn": { "field": "embedding", "query_vector": [0.12, ...], "k": 50, "num_candidates": 200 } }
      ],
      "rank_window_size": 50,
      "rank_constant": 60
    }
  }
}
```
Older way: put `query` and `knn` in the same request → ES **adds** the scores (use `boost` to weight them). Adding raw
BM25 scores (0–20+) to cosine scores (0–1) is fragile, which is why **RRF** (rank-based, step 29) is preferred.
(Check your license/version: some RRF features were paid tiers in older releases.)

### 6.5 Useful ES features for RAG
- **`highlight`**: returns the matching snippet → great for showing citations.
- **`fuzziness: "AUTO"`**: typo tolerance.
- **Aggregations**: facets ("how many docs per department") for UI or for an agent.
- **Index aliases**: build `docs_v2` with a new embedding model in the background, then switch alias `docs` → `docs_v2` in one atomic call. Zero-downtime re-index.
- **Ingest pipelines / inference endpoints**: ES can call an embedding model itself at index time.
- **Semantic reranking**: ES can call a reranker model as a final step (`text_similarity_reranker` retriever).

---

## 7. Learned sparse retrieval: SPLADE / ELSER (the "best of both")

Dense vectors = meaning, but opaque. BM25 = exact, but no synonyms. **Learned sparse** models output a
**sparse vector of weighted words**, including words that are *not in the text* but related:

```
"How do I reset my VPN password?" → { vpn: 2.1, password: 1.9, reset: 1.6, login: 0.8, credential: 0.7, remote: 0.4 }
```
- Stored in an **inverted index** like BM25 → fast, explainable, filters work.
- Learns synonyms/expansions like dense models.
- Examples: **SPLADE**, Elastic's **ELSER** (`sparse_vector` field + `sparse_vector` query).

---

## Revision notes
- **Inverted index** = textbook index: term → list of docs. Analyzer pipeline: char filters → tokenizer → token filters (lowercase, stop words, **stemming**, **synonyms**). Same analysis at index and query time.
- TF-IDF: frequent in doc + rare in corpus = important. BM25 adds **saturation (`k1`=1.2)** and **length normalisation (`b`=0.75)**.
- Memory hook: **"Rare, Repeated (but saturating), Short."**
- BM25 is great for **exact tokens** (IDs, names, codes), weak on **synonyms/meaning**.
- ES: index/document/field/mapping, **shards** (scale) & **replicas** (HA), `text` vs `keyword`, **query vs filter** context.
- ES does BM25 + `dense_vector` kNN (HNSW, `num_candidates`) + **pre-filters** + hybrid via **RRF retriever**.
- Learned sparse (SPLADE/ELSER) = inverted index + learned synonyms.

---
✅ **Done with 28.** Next: [29 Hybrid search & reranking →](29_hybrid_search_and_reranking.md)
