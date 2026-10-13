"""Elasticsearch for RAG: BM25, kNN vectors, filters (ACL), and hybrid search with RRF.

Theory: ../28_bm25_and_elasticsearch.md

Run:
    cd 07_RAG_Mastery/elasticsearch_lab
    docker compose up -d                 # start Elasticsearch (wait ~30 s)
    uv add "elasticsearch>=8.15,<9"      # Python client, once (run from the AgenticAI folder)
    uv run python es_hybrid_demo.py
"""

import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer  # import torch-based libs first (see hybrid_search.py)
from elasticsearch import Elasticsearch, helpers

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hybrid_search import load_on_cpu  # noqa: E402
from nimbus_corpus import DOCS  # noqa: E402

INDEX = "company-docs"
es = Elasticsearch("http://localhost:9200")
embedder = load_on_cpu(SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu"))


def embed(text: str) -> list[float]:
    return embedder.encode(text, normalize_embeddings=True).tolist()


# ---------------------------------------------------------------- 1. Create the index (mapping = schema)
def create_index() -> None:
    if es.indices.exists(index=INDEX):
        es.indices.delete(index=INDEX)
    es.indices.create(
        index=INDEX,
        settings={
            "number_of_shards": 1,
            "number_of_replicas": 0,  # single node: no place for a replica
            "analysis": {
                "filter": {
                    "company_synonyms": {"type": "synonym_graph", "synonyms": [
                        "vacation, holiday, pto, annual leave", "maternity, parental", "wifi, broadband, internet"]},
                },
                "analyzer": {
                    "en_search": {"tokenizer": "standard", "filter": ["lowercase", "company_synonyms", "porter_stem"]},
                    "en_index": {"tokenizer": "standard", "filter": ["lowercase", "porter_stem"]},
                },
            },
        },
        mappings={
            "properties": {
                "title": {"type": "text", "analyzer": "en_index", "search_analyzer": "en_search"},
                "content": {"type": "text", "analyzer": "en_index", "search_analyzer": "en_search"},
                "department": {"type": "keyword"},          # exact value → filters / aggregations
                "allowed_groups": {"type": "keyword"},      # ACL
                "updated_at": {"type": "date"},
                "embedding": {"type": "dense_vector", "dims": 384, "index": True, "similarity": "cosine"},
            }
        },
    )


# ---------------------------------------------------------------- 2. Index the documents (bulk)
def index_docs() -> None:
    def actions():
        for d in DOCS:
            # Toy ACL: Product docs are for support staff only, everything else for all employees
            groups = ["support"] if d["department"] == "Product" else ["all_employees", "support"]
            yield {"_index": INDEX, "_id": d["id"], "_source": {
                "title": d["title"], "content": d["text"], "department": d["department"],
                "allowed_groups": groups, "updated_at": d["updated_at"],
                "embedding": embed(f"{d['title']}. {d['text']}")}}

    ok, _ = helpers.bulk(es, actions())
    es.indices.refresh(index=INDEX)  # make the docs searchable now (normally ~1 s "near real-time")
    print(f"indexed {ok} docs")


def show(title: str, resp) -> None:
    print(f"\n== {title}")
    for h in resp["hits"]["hits"]:
        score = f"{h['_score']:.3f}" if h.get("_score") is not None else "  -  "
        print(f"  {score}  {h['_id']:<22} {h['_source']['title']}")


SOURCE = ["title"]  # only return the title field (keeps responses small)


# ---------------------------------------------------------------- 3. BM25 with field boost + filters
def bm25(query: str, groups: list[str], k: int = 5):
    return es.search(index=INDEX, size=k, source=SOURCE, query={
        "bool": {
            "must": [{"multi_match": {"query": query, "fields": ["title^2", "content"]}}],
            "filter": [{"terms": {"allowed_groups": groups}}],  # filter context: no scoring, cached
        }
    })


# ---------------------------------------------------------------- 4. kNN (HNSW) with the same pre-filter
def knn(query: str, groups: list[str], k: int = 5):
    return es.search(index=INDEX, size=k, source=SOURCE, knn={
        "field": "embedding", "query_vector": embed(query), "k": k, "num_candidates": 50,
        "filter": {"terms": {"allowed_groups": groups}},
    })


# ---------------------------------------------------------------- 5. Hybrid with the RRF retriever (ES >= 8.14)
def hybrid_rrf(query: str, groups: list[str], k: int = 5):
    acl = {"terms": {"allowed_groups": groups}}
    return es.search(index=INDEX, size=k, source=SOURCE, retriever={
        "rrf": {
            "retrievers": [
                {"standard": {"query": {"bool": {
                    "must": [{"multi_match": {"query": query, "fields": ["title^2", "content"]}}], "filter": [acl]}}}},
                {"knn": {"field": "embedding", "query_vector": embed(query), "k": 20, "num_candidates": 50,
                         "filter": acl}},
            ],
            "rank_window_size": 20,
            "rank_constant": 60,
        }
    })


def hybrid_client_side(query: str, groups: list[str], k: int = 5) -> list[str]:
    """Fallback if your ES version/licence has no RRF retriever: run both searches, fuse in Python."""
    scores: dict[str, float] = {}
    for resp in (bm25(query, groups, 20), knn(query, groups, 20)):
        for rank, h in enumerate(resp["hits"]["hits"], start=1):
            scores[h["_id"]] = scores.get(h["_id"], 0) + 1 / (60 + rank)
    return sorted(scores, key=scores.get, reverse=True)[:k]


if __name__ == "__main__":
    print(es.info()["version"]["number"])
    create_index()
    index_docs()

    support, employee = ["support"], ["all_employees"]

    show("BM25: 'E-4120' (exact code)", bm25("E-4120", support))
    show("BM25 + synonyms: 'vacation days' (index says 'annual leave')", bm25("vacation days", employee))
    show("kNN: 'Is beer covered when travelling?'", knn("Is beer covered when travelling?", employee))
    show("ACL: employee searches 'E-4021' (Product docs are support-only)", bm25("E-4021", employee))

    q = "my card was declined at checkout"
    try:
        show(f"Hybrid RRF retriever: {q!r}", hybrid_rrf(q, support))
    except Exception as e:  # older version / licence without RRF
        print(f"\nRRF retriever not available ({type(e).__name__}); fusing on the client instead:")
        print("  ", hybrid_client_side(q, support))

    # Show which words matched and why (great for debugging BM25)
    resp = es.search(index=INDEX, size=1, query={"match": {"content": "vacation days"}},
                     highlight={"fields": {"content": {}}})
    print("\n== highlight:", resp["hits"]["hits"][0]["highlight"]["content"])
