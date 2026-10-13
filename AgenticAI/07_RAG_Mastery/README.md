[🏠 Course roadmap](../README.md)

# Part 7 · RAG Mastery: from "what is RAG" to agentic search

The goal: be able to **build**, **debug** and **explain in an interview** any RAG or agentic search system.
Read the guides in order (each ends with *Revision notes*), then do the labs. The labs use one small fake company
knowledge base ([nimbus_corpus.py](nimbus_corpus.py)) with built-in traps: synonyms, look-alike error codes, an
outdated policy version, and a multi-hop question.

Prerequisite: [15c RAG basics](../02_LangChain/15c_rag.ipynb) (load → split → embed → store → retrieve).

```
 THEORY (read)                                                     PRACTICE (run)
 25 Big picture ─► 26 Ingestion & chunking ─► 27 Embeddings &      35 🔌 Search engine from scratch
                                              vector search             (BM25, RRF, MMR, metrics)
 ─► 28 BM25 & Elasticsearch ─► 29 Hybrid search & reranking        36 Hybrid + cross-encoder, measured
 ─► 30 Query transformation & routing ─► 31 Problems & fixes            (no API key)
 ─► 32 Agentic RAG & agentic search ─► 33 Evaluation & production  37 Agentic RAG in LangGraph
 ─► 34 Interview questions (70 Q&A)                                     (CRAG, search agent, router)
                                                                   ES  Elasticsearch hybrid demo
```

## Guides
| Step | Guide | You'll learn |
|---|---|---|
| 25 | [RAG: the big picture](25_rag_big_picture.md) | why RAG, the 2 pipelines, the retrieval funnel, naive → advanced → agentic, RAG vs fine-tuning vs long context |
| 26 | [Ingestion & chunking](26_ingestion_and_chunking.md) | parsing PDFs/tables, cleaning, metadata, 10 chunking strategies, parent-child, contextual retrieval, keeping the index fresh |
| 27 | [Embeddings & vector search](27_embeddings_and_vector_search.md) | embeddings, cosine, bi-encoders, choosing a model, **HNSW / IVF / PQ**, vector DBs, pre- vs post-filtering, dense weak spots |
| 28 | [BM25 & Elasticsearch](28_bm25_and_elasticsearch.md) | inverted index, analyzers, TF-IDF, **BM25 step by step**, `k1`/`b`, ES shards/mappings/query DSL, kNN, hybrid, SPLADE/ELSER |
| 29 | [Hybrid search & reranking](29_hybrid_search_and_reranking.md) | **RRF**, score fusion, **bi-encoder vs cross-encoder**, ColBERT, LLM rerankers, MMR, lost in the middle |
| 30 | [Query transformation & routing](30_query_transformation_and_routing.md) | conversational rewrite, multi-query, RAG-Fusion, **HyDE**, decomposition, step-back, self-query filters, routers |
| 31 | [RAG problems & fixes](31_rag_problems_and_fixes.md) | **debugging ladder**, 7 failure points, 40+ problems with symptom → cause → fix, hallucination defence, security |
| 32 | [Agentic RAG & agentic search](32_agentic_rag_and_agentic_search.md) | ReAct retrieval, **CRAG**, **Self-RAG**, **Adaptive RAG**, multi-hop, deep research, GraphRAG, grep-style search, tool design |
| 33 | [Evaluation & production](33_evaluation_and_production.md) | Recall@k, MRR, nDCG, faithfulness, RAGAS, eval sets, latency, caching, ACLs, monitoring, checklist |
| 34 | [Interview questions](34_interview_questions.md) | **70 questions** with collapsible answers + 2-minute rapid-fire revision |

## Labs
| Step | Lab | Needs |
|---|---|---|
| 35 | 🔌 [Search engine from scratch](35_lab_search_from_scratch.ipynb): analyzer, inverted index, BM25, `k1`/`b`, RRF, metrics, MMR | nothing (pure Python) |
| 36 | [Hybrid + rerank pipeline](36_lab_hybrid_rerank_pipeline.ipynb): BM25 vs dense vs hybrid vs cross-encoder, per question; HNSW recall; abstain threshold | no API key (downloads ~100 MB of models once) |
| 37 | [Agentic RAG with LangGraph](37_lab_agentic_rag_langgraph.ipynb): grounded baseline, **CRAG graph**, search agent with ACL, adaptive router | `OPENAI_API_KEY` |
| ES | [Elasticsearch hybrid demo](elasticsearch_lab/es_hybrid_demo.py): mapping, synonyms, BM25 + kNN + ACL filters, RRF retriever | Docker + `uv add "elasticsearch>=8.15,<9"` |

Helper modules: [nimbus_corpus.py](nimbus_corpus.py) (docs + 21 labelled questions), [hybrid_search.py](hybrid_search.py) (the lab-36 stack, importable).

What lab 36 shows on the 21 labelled questions:

| Stage | hit@1 | MRR |
|---|---|---|
| BM25 | 0.76 | 0.84 |
| Dense (MiniLM) | 0.81 | 0.91 |
| Hybrid (RRF) | 0.86 | 0.91 |
| + Cross-encoder rerank | **1.00** | **1.00** |

BM25 misses synonyms and dense misses look-alike codes. They fail on different questions, which is why hybrid wins and the reranker fixes the order.

> **macOS note:** the labs run models on CPU and import `sentence_transformers` before `faiss`, and set
> `faiss.omp_set_num_threads(1)`. Without that, FAISS and PyTorch can crash each other (OpenMP clash), and some
> torch/transformers versions return NaN on CPU unless weights are copied into RAM (`load_on_cpu`).

Visual one-page revision with a k1 slider and flashcards: [RAG Mastery Map](https://claude.ai/artifact/VcDGEAnmRwK91Wzj3GbxyD) (private claude.ai page).

## The 12 things to remember (if you forget everything else)
1. **RAG = open-book exam.** RAG for knowledge, fine-tuning for behaviour.
2. Two pipelines: **indexing** (load → clean → chunk → embed → store) and **query** (**T-R-F-R-G**: transform → retrieve → fuse → rerank → generate).
3. **Funnel:** cheap search for recall (top 50) → cross-encoder for precision (top 5) → LLM.
4. **Garbage in, garbage out:** look at your parsed chunks; metadata = citations + filters + ACL + freshness.
5. Chunking: start recursive ~500 tokens / 10–15% overlap; structure-aware, **parent-child**, **contextual headers** when needed.
6. **BM25 = Rare, Repeated (saturating), Short.** Great for exact tokens, blind to synonyms.
7. **Dense = meaning**, weak on codes/names/negation/numbers. **HNSW**: `ef_search` ↑ = recall ↑, speed ↓.
8. **Hybrid + RRF** (Σ 1/(60+rank), rewards agreement) is the default upgrade.
9. **Cross-encoder** reads query+doc together: accurate, slow → rerank only the top candidates; its score is an abstain signal.
10. Debug ladder: **Exists → Parsed → Found → Ranked → Used → Shown.** Fix retrieval before prompts.
11. **ACL at retrieval time** in code, never in the prompt. Retrieved text can carry **prompt injection**.
12. Agentic RAG = **Think → Search → Read → Decide → Answer**; CRAG grades and retries; cap loops; measure answers, trajectories and cost.
