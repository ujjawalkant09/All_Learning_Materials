**Part 7 · RAG Mastery** · step 34 of 37
[← 33 Evaluation & production](33_evaluation_and_production.md) · [🏠 Roadmap](../README.md) · [35 Lab: search from scratch →](35_lab_search_from_scratch.ipynb)

# 34 · RAG & Agentic Search Interview Questions (70 Q&A)

> **How to use:** read the question, **answer out loud first**, then click to open the answer.
> ⭐ = asked very often. Each answer is short on purpose: this is how you'd say it in an interview.
> The numbers in [brackets] point to the guide with the details.

---

## A. Fundamentals

<details><summary>⭐ 1. What is RAG and why use it?</summary>

Retrieval-Augmented Generation: retrieve relevant chunks from our own data, put them in the prompt, and let the
LLM answer **grounded** in them, with citations. It solves private data, knowledge cutoff, hallucination, missing
sources, and scale (we can't fit all docs in the prompt). It's an open-book exam for the LLM. [25]
</details>

<details><summary>⭐ 2. Draw/describe a RAG pipeline end to end.</summary>

**Indexing (offline):** load → parse → clean → chunk → embed → store in a vector index and a keyword (BM25) index, with metadata.
**Query (online):** transform query (rewrite) → retrieve with BM25 + dense (with filters) → fuse with RRF → rerank
with a cross-encoder → build a prompt with the top chunks and citations → LLM generates → (optional) faithfulness check. [25]
</details>

<details><summary>⭐ 3. RAG vs fine-tuning: when do you use which?</summary>

RAG for **knowledge** (facts that change, need citations, per-user access control). Fine-tuning for **behaviour**
(style, format, domain language, task skill). They combine well. Fine-tuning to add facts is costly, goes stale,
can't cite, and can't respect access control. [25]
</details>

<details><summary>4. RAG vs long-context models: is RAG dead with 1M-token windows?</summary>

No. Long context costs money and time on every call, quality drops for information in the middle, and you still
can't fit a whole company's data or apply per-user permissions. Long context is great for "analyse these few
documents now"; RAG for large, changing knowledge bases. They also combine: retrieve more, bigger chunks, because the window is larger. [25]
</details>

<details><summary>5. When should you NOT use RAG?</summary>

Aggregations over structured data (use SQL), tasks that need the whole document (summarise this contract →
full doc / map-reduce), general knowledge the model already has, or when latency must be minimal and the data is tiny (just put it in the prompt).
</details>

<details><summary>6. What are naive, advanced and agentic RAG?</summary>

Naive: chunk → embed → top-k → stuff. Advanced: better chunking, hybrid search, reranking, query rewriting,
filters, evaluation. Agentic: an LLM agent decides whether/what/where to search, iterates, grades results, and stops when it has enough. [25, 32]
</details>

## B. Ingestion & chunking

<details><summary>⭐ 7. How do you choose chunk size and overlap?</summary>

Trade-off: small chunks are precise but lose context; big chunks keep context but add noise and cost. Start ~400–800
tokens with 10–15% overlap, respect structure (headings, paragraphs), then **tune on an eval set** (recall@k, faithfulness).
FAQs → small; legal/research → bigger or parent-child. Chunk must fit the embedding model's max input. [26]
</details>

<details><summary>8. Name chunking strategies.</summary>

Fixed-size, recursive character (default), structure/document-aware (headings, code functions), semantic (split
where meaning changes), parent-child / small-to-big, sentence-window, contextual chunk headers / contextual
retrieval, late chunking, proposition chunking. [26]
</details>

<details><summary>⭐ 9. What is parent-child (small-to-big) retrieval?</summary>

Index small child chunks for precise matching, but return the larger parent section to the LLM for full context.
Child metadata stores `parent_id`. Solves "precise match but missing context". [26]
</details>

<details><summary>10. What is Contextual Retrieval?</summary>

Before indexing, prepend a short LLM-written context to each chunk ("This chunk is from ACME's Q2 2025 report,
section revenue...") and build both embeddings and BM25 on it. Fixes chunks that lost their subject. Prompt caching
keeps the cost low. It noticeably reduced retrieval failures in Anthropic's experiments, more so combined with reranking. [26]
</details>

<details><summary>11. How do you handle tables, images and scanned PDFs?</summary>

Tables: extract as markdown/HTML, repeat headers when splitting, add an LLM summary chunk, or route numeric questions to SQL.
Images: caption with a vision model and index the caption (or multimodal embeddings). Scanned PDFs: OCR or a vision LLM. [26]
</details>

<details><summary>12. Why is metadata important?</summary>

Citations (source, page), filters (department, date, type), **access control** (allowed groups, tenant), freshness
(updated_at, version), and updates/deletes (doc_id). [26]
</details>

<details><summary>13. How do you keep the index up to date?</summary>

Stable `doc_id` + content hash. On sync: changed hash → delete old chunks, insert new; unchanged → skip; deleted at source → delete.
LangChain indexing API + RecordManager does this. Changing embedding model → full re-embed into a new index, then alias swap. [26, 28]
</details>

## C. Embeddings & vector search

<details><summary>⭐ 14. What is an embedding? How is similarity measured?</summary>

A vector that represents meaning; similar texts are close. Cosine similarity (angle) is standard; with normalised
vectors, dot product gives the same ranking and is faster. [27]
</details>

<details><summary>15. How do you choose an embedding model?</summary>

MTEB retrieval scores as a shortlist, then test on **your** eval set. Consider max input length, dimensions/storage,
language support, hosted vs local (privacy/cost), query/passage prefixes, latency. Same model for queries and docs. [27]
</details>

<details><summary>⭐ 16. Explain HNSW.</summary>

A multi-layer graph: top layers have few nodes with long links (highways), bottom layer has all nodes with short links (streets).
Search starts at the top, greedily moves to closer nodes, goes down a layer, repeats. Params: `M` (links per node),
`ef_construction` (build quality), `ef_search` (query candidates; higher = better recall, slower). Fast and accurate, RAM-hungry. [27]
</details>

<details><summary>17. Explain IVF and PQ.</summary>

IVF: k-means clusters; search only the `nprobe` nearest clusters. PQ: compress vectors by splitting into sub-vectors
and storing the id of the nearest centroid for each part; huge memory savings, some accuracy loss. Often IVF-PQ together. [27]
</details>

<details><summary>18. Exact vs approximate nearest neighbour search?</summary>

Exact (flat) compares with all vectors: perfect recall, fine up to ~100k vectors. ANN trades a little recall for
huge speed on millions/billions. Measure ANN recall against exact search. [27]
</details>

<details><summary>19. Pre-filtering vs post-filtering?</summary>

Post-filter: get top-k, then remove those failing the filter → may return few or zero. Pre-filter / filtered ANN:
apply the filter during search → k valid results. Prefer pre-filtering, especially for ACLs. [27]
</details>

<details><summary>⭐ 20. Where does dense retrieval fail?</summary>

Exact tokens (IDs, codes, names), rare jargon, negation, numbers/dates, out-of-domain text, very long chunks, and
"similar but not relevant". Fixes: hybrid with BM25, metadata filters, reranking, fine-tuned embeddings. [27]
</details>

<details><summary>21. Which vector DB would you pick?</summary>

Depends: FAISS for local/library use, pgvector if we already use Postgres, Elasticsearch/OpenSearch if we need strong
BM25 + vectors + filters + aggregations, Qdrant/Weaviate/Milvus for dedicated vector scale, Pinecone for managed.
Criteria: filtering, hybrid support, scale, ops, cost, multi-tenancy, existing stack. [27]
</details>

<details><summary>22. How would you fine-tune an embedding model?</summary>

Collect (query, relevant passage) pairs from logs or generate them synthetically, mine hard negatives (similar but
wrong passages, e.g. from BM25), train with a contrastive loss (e.g. MultipleNegativesRankingLoss in
sentence-transformers), evaluate recall@k before/after, then re-index everything.
</details>

## D. BM25 & Elasticsearch

<details><summary>⭐ 23. Explain BM25.</summary>

A keyword ranking function: sum over query terms of IDF × saturated TF with length normalisation. Rare terms count
more (IDF), repeats help with diminishing returns (`k1`≈1.2), and matches in shorter docs count more (`b`≈0.75).
Hook: "Rare, Repeated but saturating, Short." [28]
</details>

<details><summary>24. What do k1 and b control?</summary>

`k1` = how fast term-frequency saturates (0 = only presence matters, higher = repeats matter more).
`b` = length normalisation (0 = ignore length, 1 = full normalisation). [28]
</details>

<details><summary>25. BM25 vs TF-IDF?</summary>

Both use TF × IDF. BM25 caps the TF effect (saturation) and normalises by document length relative to the average, so it doesn't reward keyword stuffing or long docs. [28]
</details>

<details><summary>⭐ 26. What is an inverted index?</summary>

A map from each term to the list of documents (and positions/frequencies) that contain it, like a book's index.
Query time only reads the lists for query terms, so it's very fast. [28]
</details>

<details><summary>27. What is an analyzer in Elasticsearch?</summary>

Char filters → tokenizer → token filters (lowercase, stop words, stemming, synonyms). It turns text into terms. Index and query text must be analyzed compatibly, or matches fail. [28]
</details>

<details><summary>28. `text` vs `keyword` field?</summary>

`text` is analyzed for full-text BM25 search. `keyword` is exact, for filters, sorting and aggregations. Use multi-fields to have both. [28]
</details>

<details><summary>29. Query context vs filter context?</summary>

Query context scores documents (how well?). Filter context is yes/no, not scored, and cached, so it is faster. Put ACLs, dates, categories in `filter`. [28]
</details>

<details><summary>30. Shards and replicas?</summary>

Shards split an index for horizontal scale (each is a Lucene index). Replicas are copies for availability and read throughput.
A search fans out to shards and merges the top results. [28]
</details>

<details><summary>⭐ 31. How do you do hybrid search in Elasticsearch?</summary>

Mapping with a `text` field (BM25) and a `dense_vector` field (HNSW). Run a `match` query and a `knn` query and combine
them with the **RRF retriever** (newer versions), or add boosted scores in the older combined `query` + `knn` request.
Apply the same filters to both. [28]
</details>

<details><summary>32. What is `num_candidates` in ES kNN?</summary>

The number of nearest-neighbour candidates considered per shard during HNSW search (similar to `ef_search`). Higher = better recall, slower. `k` = how many to return. [28]
</details>

<details><summary>33. What is SPLADE / ELSER (learned sparse retrieval)?</summary>

A model outputs a sparse vector of weighted terms, including related terms not in the text (expansion). Stored in an
inverted index: fast, explainable, filterable like BM25, but with learned synonyms like dense. [28]
</details>

## E. Hybrid search & reranking

<details><summary>⭐ 34. Why hybrid search?</summary>

BM25 catches exact terms; dense catches meaning/synonyms. They fail on different queries, so combining is more robust and usually beats either alone. [29]
</details>

<details><summary>⭐ 35. Explain Reciprocal Rank Fusion.</summary>

For each document: sum over result lists of 1/(k + rank), k usually 60. It uses ranks only, so scores on different
scales don't matter, no tuning needed, and docs found by several retrievers rise. "RRF rewards agreement." [29]
</details>

<details><summary>36. Alternatives to RRF?</summary>

Normalise scores (min-max or z-score) and take a weighted sum (convex combination). Can be better if tuned on eval data, but sensitive to score distributions/outliers. [29]
</details>

<details><summary>⭐ 37. Bi-encoder vs cross-encoder?</summary>

Bi-encoder encodes query and doc separately → doc vectors precomputed → fast retrieval over millions, less accurate.
Cross-encoder feeds query+doc together through one transformer → full attention between them → much more accurate,
but must run per pair at query time → only for reranking the top 20–100. [29]
</details>

<details><summary>38. What is ColBERT / late interaction?</summary>

One vector per token; score = sum over query tokens of the max similarity with any doc token (MaxSim). Docs are precomputed like a bi-encoder, with near cross-encoder quality; storage is large. [29]
</details>

<details><summary>39. How many documents to rerank? How to pick k?</summary>

Retrieve 20–100 (enough for recall), rerank, keep 3–10 for the LLM (enough to answer, little noise). Tune on recall@N for the first stage, and MRR/faithfulness/latency for the final k. [29]
</details>

<details><summary>40. What is MMR?</summary>

Maximal Marginal Relevance: choose the next doc by relevance to the query minus similarity to docs already chosen. Reduces duplicates, increases coverage. [29]
</details>

<details><summary>41. What is "lost in the middle"?</summary>

LLMs use information at the start and end of long contexts better than the middle. Send fewer, reranked chunks, put the best first, and label them for citation. [29]
</details>

<details><summary>42. Can an LLM be a reranker?</summary>

Yes: pointwise (score each), pairwise (compare two), listwise (order a list). Smart and instructable but slow/costly and position-biased; often used after a cross-encoder on the final few. [29]
</details>

## F. Query transformation

<details><summary>⭐ 43. What is HyDE?</summary>

Hypothetical Document Embeddings: the LLM writes a fake answer, we embed that and search with it. Answer-to-answer
similarity beats question-to-answer. Risk: misleading fake answers in unknown domains; extra latency. [30]
</details>

<details><summary>44. Multi-query and RAG-Fusion?</summary>

Generate several rephrasings, retrieve for each, merge. RAG-Fusion merges with RRF. Fixes vocabulary mismatch at the cost of more calls. [30]
</details>

<details><summary>⭐ 45. How do you handle follow-up questions in a chatbot?</summary>

Conversational query rewriting: LLM turns "and for interns?" + history into a standalone query, search with it, then answer with history in the prompt. [30]
</details>

<details><summary>46. Query decomposition vs step-back?</summary>

Decomposition splits a complex question into sub-questions (parallel or sequential/multi-hop). Step-back asks a more
general question to retrieve background principles, then answers the specific one. [30]
</details>

<details><summary>47. What is self-query retrieval?</summary>

The LLM extracts metadata filters from the question ("docs from 2025 by security" → `{year:2025, dept:security}`) using structured output, plus a semantic query. Validate values; never execute raw LLM-written filters. [30]
</details>

<details><summary>48. How do you route between multiple data sources?</summary>

Rules, semantic router (embedding similarity to route examples), a classifier, an LLM with structured output, or an agent with each source as a tool. Trade-off: cost/latency vs flexibility. [30]
</details>

## G. Problems, debugging & hallucination

<details><summary>⭐ 49. Your RAG gives wrong answers. How do you debug?</summary>

Walk the ladder: Is the answer in the corpus? Parsed/chunked well? In top-50 (recall)? In top-5 (ranking)? Did
the LLM use it (generation)? Correct format/citations? Log retrieved chunks per request and measure recall@k on an eval set.
Retrieval vs generation first. [31]
</details>

<details><summary>⭐ 50. How do you reduce hallucinations in RAG?</summary>

Better retrieval (hybrid + rerank), strict grounded prompt with "I don't know" path, temperature 0, cite every claim,
validate citations, faithfulness check (LLM judge/NLI) with regenerate, abstain on low reranker scores, show sources, measure faithfulness. [31]
</details>

<details><summary>51. What are the 7 failure points of RAG?</summary>

Missing content, missed top-ranked docs, not in context (consolidation), not extracted, wrong format, incorrect specificity, incomplete answer. [31]
</details>

<details><summary>52. How do you handle conflicting or outdated documents?</summary>

Ingestion: keep latest version, delete removed docs, `version`/`updated_at` metadata. Retrieval: filter or boost recent.
Generation: show dates in context, instruct to prefer newest and mention conflicts. [31]
</details>

<details><summary>53. How do you answer "summarise the main themes across all documents"?</summary>

Top-k retrieval can't, because the answer is spread across everything. Use map-reduce summarisation, precomputed hierarchical summaries (RAPTOR-style), or GraphRAG global search over community summaries. [31, 32]
</details>

<details><summary>54. User asks "how many tickets were opened in May?"</summary>

That's aggregation over structured data → route to a SQL tool (text-to-SQL with a read-only connection), not vector search. [31]
</details>

<details><summary>⭐ 55. How do you enforce access control in RAG?</summary>

Store ACL metadata on each chunk (`allowed_groups`, `tenant_id`), and apply it as a **pre-filter in the search
query** using the user's identity from a trusted source (auth/runtime context), never from the model. Separate
indexes per tenant for strong isolation. Never rely on the prompt to hide data. [31, 33]
</details>

<details><summary>56. What is indirect prompt injection in RAG and how do you mitigate it?</summary>

Malicious instructions hidden in documents/web pages that the LLM reads as context. Mitigate: treat context as data
(delimiters + instruction), least-privilege tools, human approval for risky actions, output filtering, trusted sources only, monitoring. [31, 33]
</details>

## H. Agentic RAG & agentic search

<details><summary>⭐ 57. What is agentic RAG? When would you use it?</summary>

The LLM controls retrieval in a loop: decides if/what/where to search, reads, refines, stops. Use for multi-part,
multi-hop, multi-source, ambiguous questions. Costs more latency/tokens, less predictable; start with 2-step RAG. [32]
</details>

<details><summary>⭐ 58. Explain Corrective RAG (CRAG).</summary>

After retrieval, grade each doc's relevance. All good → generate. Some → keep good ones and supplement. None → rewrite
the query and retrieve again or fall back to web search. Max retries, then abstain. [32]
</details>

<details><summary>59. Explain Self-RAG.</summary>

The model reflects: should I retrieve? is this passage relevant? is my answer supported? is it useful? If not
grounded → regenerate; if not useful → rewrite/retrieve again. Originally trained reflection tokens; in practice LLM-judge nodes in a graph. [32]
</details>

<details><summary>60. Explain Adaptive RAG.</summary>

Classify question complexity first: no retrieval for simple/general, single-shot RAG for single facts, iterative/agentic RAG for complex ones. Spends effort only where needed. [32]
</details>

<details><summary>61. How does a "deep research" agent work?</summary>

A planner breaks the question into sub-questions; parallel sub-agents search and read with separate contexts and
return compressed findings with citations; a synthesiser writes the report and can trigger more research for gaps. Expensive but powerful. [32]
</details>

<details><summary>62. What is GraphRAG?</summary>

Extract entities/relations into a knowledge graph. Local search walks relations from entities in the question (multi-hop). Global search uses community summaries to answer corpus-wide questions. Indexing is expensive. [32]
</details>

<details><summary>63. Why do coding agents often use grep instead of a vector DB?</summary>

Code has exact symbols and structure; grep/glob/read is always fresh (no index sync), exact, and the agent can follow
references iteratively. Vector search helps for fuzzy natural-language lookups in huge codebases. Retrieval ≠ vector DB. [32]
</details>

<details><summary>⭐ 64. How do you design search tools for an agent?</summary>

Clear names/docstrings, few distinct tools, search returns compact cited snippets + ids, a separate fetch tool for
full docs, filters as typed params, helpful error messages, result limits, and ACLs enforced inside the tool from trusted context. [32]
</details>

<details><summary>65. How do you stop an agent from looping or overspending?</summary>

Max iterations / recursion limit, token and time budgets in state, rewrite from the original question (avoid drift),
cheaper models for grading, abstain after N failures, monitor tool-call counts. [32]
</details>

<details><summary>66. Workflow (graph) vs agent for RAG?</summary>

If the steps can be drawn in advance (retrieve → grade → rewrite → retry), use a LangGraph workflow: predictable,
testable. If steps are unknown, use an agent. CRAG/Self-RAG = graph with LLM decisions on edges. [32]
</details>

## I. Evaluation & production

<details><summary>⭐ 67. How do you evaluate a RAG system?</summary>

Separately: retrieval (recall@k, MRR, nDCG, hit rate on labelled question → source pairs) and generation
(faithfulness, answer relevance, context precision/recall, correctness via LLM-as-judge calibrated on human labels).
Eval set of real + hard + reviewed synthetic questions, run in CI, add failures. Plus latency and cost. Tools: RAGAS, DeepEval, LangSmith. [33]
</details>

<details><summary>68. Recall@k vs MRR vs nDCG?</summary>

Recall@k: fraction of relevant docs found in top-k. MRR: 1/rank of the first relevant, averaged. nDCG: rewards relevant docs higher in the list, supports graded relevance. "Found? How fast? Good order?" [33]
</details>

<details><summary>69. How do you reduce RAG latency?</summary>

Stream tokens, parallel retrievers, skip unneeded rewrites, smaller/faster reranker or fewer candidates, ANN tuning,
caching (embedding, exact, semantic with care), smaller models for side tasks, shorter prompts. [33]
</details>

<details><summary>⭐ 70. Design a RAG system for 10M internal documents with per-team permissions.</summary>

Ingestion: connectors → parser (OCR, tables) → clean/dedupe → structure-aware chunks with contextual headers →
metadata (doc_id, source, dates, `allowed_groups`) → batch embeddings → Elasticsearch/OpenSearch (BM25 + HNSW, sharded,
replicas), incremental sync by hash, alias swap for re-index.
Query: auth → conversational rewrite + self-query filters → hybrid BM25 + kNN with ACL pre-filter → RRF top-50 →
cross-encoder top-5 + threshold → grounded prompt with citations → streaming LLM → faithfulness check.
Agentic layer for complex questions (CRAG loop, SQL tool for aggregates). Ops: eval set in CI, tracing, dashboards,
feedback, caching, prompt-injection defences, cost monitoring. [25–33]
</details>

---

## Rapid-fire one-liners (revise in 2 minutes)
- RAG = **open-book exam**. RAG for knowledge, fine-tuning for behaviour.
- Pipeline = **T-R-F-R-G**: Transform, Retrieve, Fuse, Rerank, Generate.
- Funnel: cheap on many (BM25/ANN top-50) → expensive on few (cross-encoder top-5) → LLM.
- BM25 = **Rare, Repeated (saturating), Short**. `k1`=1.2, `b`=0.75.
- RRF = Σ 1/(60 + rank) → **rewards agreement**.
- Bi-encoder = CV keyword filter; cross-encoder = manager reading CVs.
- HNSW = highways → roads → streets. `ef_search`↑ = recall↑ latency↑.
- HyDE = search with a fake answer to find the real one.
- Debug ladder: **Exists → Parsed → Found → Ranked → Used → Shown**.
- ACL = **filter at retrieval**, never in the prompt.
- Agentic = **Think → Search → Read → Decide → Answer**; CRAG = grade, rewrite, retry.
- Eval: **Found? How fast? Good order?** + faithfulness, relevance.

---
✅ **Done with 34.** Next: [35 Lab: search from scratch →](35_lab_search_from_scratch.ipynb)
