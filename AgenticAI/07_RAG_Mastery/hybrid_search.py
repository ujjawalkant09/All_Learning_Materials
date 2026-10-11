"""The retrieval stack from lab 36 as an importable module: BM25 + dense (FAISS) → RRF → cross-encoder rerank.

Lab 36 explains every line. Lab 37 imports it so the agent code stays short:

    from hybrid_search import HybridSearcher
    searcher = HybridSearcher(DOCS)
    hits = searcher.search("E-4210", k=3, department="Product")   # -> list[Hit]
"""

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

import numpy as np
from sentence_transformers import CrossEncoder, SentenceTransformer  # import torch-based libs BEFORE faiss:
import faiss  # noqa: E402  on macOS the reverse order can segfault (two OpenMP runtimes clash)

faiss.omp_set_num_threads(1)  # same clash at search time; 1 thread is plenty for small indexes

STOP = {"a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "is", "are", "be", "it", "my", "i", "do", "does",
        "what", "how", "can", "with", "per", "at", "by", "from", "if", "your", "you", "their"}


def stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            return word[:-1] if suffix == "ing" and word[-1] == word[-2] else word
    return word


def analyze(text: str) -> list[str]:
    toks = re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())
    return [stem(t) for t in toks if t not in STOP]


def load_on_cpu(model):
    """Copy weights into normal RAM. Workaround: with some torch/transformers versions on macOS, memory-mapped
    weights make CPU inference return NaN (seen with torch 2.14 + transformers 5.19)."""
    for p in model.parameters():
        p.data = p.data.clone()
    return model


@dataclass
class Hit:
    id: str
    title: str
    text: str
    department: str
    updated_at: str
    score: float  # cross-encoder logit: > 0 relevant, very negative = irrelevant


class HybridSearcher:
    def __init__(self, docs: list[dict],
                 embed_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: str = "cpu"):
        # CPU is plenty for these small models, and avoids macOS Metal (MPS) crashes when mixed with other libraries
        self.docs = docs
        self.texts = [f"{d['title']}. {d['text']}" for d in docs]
        # BM25 statistics
        self.tfs = [Counter(analyze(t)) for t in self.texts]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avgdl = sum(self.lens) / len(self.lens)
        df = Counter(term for tf in self.tfs for term in tf)
        self.idf = {t: math.log(1 + (len(docs) - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        # dense index
        self.embedder = load_on_cpu(SentenceTransformer(embed_model, device=device))
        vecs = self.embedder.encode(self.texts, normalize_embeddings=True, show_progress_bar=False).astype("float32")
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)
        self.reranker = CrossEncoder(rerank_model, device=device)
        load_on_cpu(self.reranker.model)

    def _bm25(self, query: str, allowed: set[int], k: int) -> list[int]:
        scores = defaultdict(float)
        for t in analyze(query):
            for i in allowed:
                tf = self.tfs[i].get(t)
                if tf:
                    norm = 1 - 0.75 + 0.75 * self.lens[i] / self.avgdl
                    scores[i] += self.idf[t] * tf * 2.2 / (tf + 1.2 * norm)
        return sorted(scores, key=scores.get, reverse=True)[:k]

    def _dense(self, query: str, allowed: set[int], k: int) -> list[int]:
        qv = self.embedder.encode([query], normalize_embeddings=True).astype("float32")
        _, idx = self.index.search(qv, len(self.docs))       # tiny corpus: score all, then filter (a real DB pre-filters)
        return [i for i in idx[0] if i in allowed][:k]

    def search(self, query: str, k: int = 4, department: str | None = None, candidates: int = 20) -> list[Hit]:
        allowed = {i for i, d in enumerate(self.docs) if department is None or d["department"] == department}
        fused = defaultdict(float)
        for lst in (self._bm25(query, allowed, candidates), self._dense(query, allowed, candidates)):
            for rank, i in enumerate(lst, start=1):
                fused[i] += 1 / (60 + rank)
        cand = sorted(fused, key=fused.get, reverse=True)[:candidates]
        if not cand:
            return []
        scores = self.reranker.predict([(query, self.texts[i]) for i in cand])
        ranked = sorted(zip(cand, scores), key=lambda x: x[1], reverse=True)[:k]
        return [Hit(self.docs[i]["id"], self.docs[i]["title"], self.docs[i]["text"], self.docs[i]["department"],
                    self.docs[i]["updated_at"], float(s)) for i, s in ranked]

    def get(self, doc_id: str) -> dict | None:
        return next((d for d in self.docs if d["id"] == doc_id), None)
