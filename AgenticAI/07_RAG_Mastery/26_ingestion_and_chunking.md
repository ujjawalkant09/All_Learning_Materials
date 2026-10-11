**Part 7 · RAG Mastery** · step 26 of 37
[← 25 Big picture](25_rag_big_picture.md) · [🏠 Roadmap](../README.md) · [27 Embeddings & vector search →](27_embeddings_and_vector_search.md)

# 26 · Ingestion & Chunking: Garbage In, Garbage Out

> **What you'll learn:** how to turn messy files into clean, searchable chunks: parsing PDFs and tables,
> cleaning, metadata, every chunking strategy (fixed, recursive, structure-aware, semantic, parent-child,
> sentence-window, contextual retrieval, late chunking), and how to choose chunk size.

**Key truth:** most "bad RAG answers" are not LLM problems. They are **ingestion** problems. If the
right text never made it into a clean chunk, no reranker or prompt can save you.

---

## 1. Loading & parsing: getting clean text out

| Source | Typical problem | What to do |
|---|---|---|
| **Digital PDF** | text order mixed up (2 columns), headers/footers on every page | `pymupdf` / `pypdf`; layout-aware parsers (Unstructured, Docling, LlamaParse) |
| **Scanned PDF** | no text at all, just images | **OCR** (Tesseract, cloud OCR) or a vision LLM |
| **Tables** | rows become a soup of numbers, meaning lost | extract table as **Markdown/HTML**, keep the header with every row-group, or write a 1-line summary of the table |
| **Images / charts** | invisible to text search | caption them with a vision model, index the caption |
| **HTML** | menus, cookie banners, ads | strip boilerplate (BeautifulSoup / trafilatura), keep `<h1>..<h3>` as structure |
| **Slides** | very little text per slide, meaning in pictures | one chunk per slide + speaker notes + slide title |
| **Code** | splitting mid-function breaks meaning | split by function/class (language-aware splitter, AST) |
| **Email / chat** | quoted replies duplicate text | remove quoted history, keep thread id as metadata |

**Rule:** always **look at your parsed text** before going further. Print 10 random chunks. You'll find problems in 2 minutes.

---

## 2. Cleaning

- Remove repeated **headers/footers/page numbers** ("Confidential – Page 3 of 40").
- Fix **hyphenation** across lines ("informa-\ntion" → "information") and broken whitespace.
- **De-duplicate**: same document in 3 folders → same chunk 3 times in your top-5 (wastes context). Use a hash of the text, or near-duplicate detection (MinHash) for "almost same".
- Normalise unicode (`ﬁ` ligature → `fi`), weird quotes, non-breaking spaces. Otherwise BM25 can't match the word.
- Drop **empty / tiny chunks** ("Table of contents", "....... 12").

---

## 3. Metadata: the secret weapon

Every chunk should carry metadata. It powers **filters**, **citations**, **access control** and **freshness**.

```python
Document(
    page_content="Employees get 24 days of paid annual leave...",
    metadata={
        "source": "hr/leave_policy_2026.pdf",   # citation
        "page": 3,                              # citation
        "section": "Annual Leave > Carry over", # breadcrumb, helps the LLM understand context
        "doc_type": "policy",                   # filter: only search policies
        "department": "HR",                     # filter / routing
        "updated_at": "2026-03-01",             # freshness: prefer newer versions
        "version": "v4",                        # avoid mixing old and new policy
        "allowed_groups": ["all_employees"],    # SECURITY: who may see this chunk
        "doc_id": "leave-policy", "chunk_id": 7 # for parent lookup, updates and deletes
    },
)
```

Without `doc_id` you can't **update or delete** a document later. Without `allowed_groups` you will leak data.

---

## 4. Why chunk at all?

1. **Embedding models have input limits** (often 512–8192 tokens) and one vector for a 50-page doc is a blurry average of everything.
2. **Precision:** we want to send the LLM the *paragraph* that answers, not the whole manual.
3. **Cost:** fewer tokens in the prompt.

### The Goldilocks problem

```
 TOO SMALL (50 tokens)                 JUST RIGHT (200–800 tokens)          TOO BIG (3000 tokens)
 "It costs 99 USD per month."          A full idea with its subject          Many topics mixed together
 → What costs 99 USD?? context lost    → self-contained, searchable          → vector is a blurry average
 → precise match, useless answer                                            → irrelevant text, high cost
```

**Starting point:** `chunk_size ≈ 400–800 tokens`, `overlap ≈ 10–15%`. Then **measure** (step 33) and tune.
- Factual Q&A (FAQ, policy) → smaller chunks (200–500).
- Questions that need reasoning over a whole section (legal, research) → bigger chunks (800–1500) or parent-child.

**Overlap** = repeat the last N tokens of chunk 1 at the start of chunk 2, so a sentence cut at the border isn't lost.
Too much overlap = duplicates in results and a bigger index.

---

## 5. Chunking strategies (from simple to smart)

### 5.1 Fixed-size
Cut every N characters/tokens. Fast and dumb; cuts sentences in half. Only for baselines.

### 5.2 Recursive character splitting ✅ default
Try to split on `"\n\n"` (paragraphs), then `"\n"`, then `". "`, then `" "`, until each piece fits.
Keeps paragraphs and sentences together most of the time.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=60)  # sizes in TOKENS
chunks = splitter.split_documents(docs)
```

### 5.3 Structure-aware (document-aware) splitting ✅ best for real docs
Split on the document's own structure: Markdown headings, HTML `<h2>`, PDF sections, code functions.
And **keep the heading path** in each chunk ("HR Policy > Leave > Carry over").

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")])
sections = md_splitter.split_text(markdown_text)        # each section has metadata {"h1":..., "h2":...}
chunks = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80).split_documents(sections)  # 2nd pass for long sections
```

### 5.4 Semantic chunking
Embed every sentence; start a new chunk where the meaning **jumps** (cosine distance between neighbour
sentences is above a threshold). Good for text with no structure (transcripts). Costs embeddings at index time; benefits are not always big, so measure.

### 5.5 Parent-child (small-to-big) retrieval ✅ very popular
**Search small, return big.**
- Index **small child chunks** (e.g. 200 tokens) → precise matching.
- When a child matches, send its **parent** (e.g. the 1500-token section) to the LLM → full context.

```
 Parent section (1500 tokens) ───────────────────────────────────────────────┐
 │ child 1 (200) │ child 2 (200) │ child 3 (200) ◄── query matches here │ ... │
 └──────────────────────────────────────────────────────────────────────────┘
                     LLM receives the WHOLE parent, not only child 3
```
LangChain: `ParentDocumentRetriever`. You can also do it yourself: store `parent_id` in child metadata.

### 5.6 Sentence-window retrieval
Index single sentences; at answer time, return the matched sentence **plus N sentences around it**. Same idea as parent-child, finer grain.

### 5.7 Contextual chunk headers / Contextual Retrieval ✅ big win, cheap
Problem: a chunk says *"Revenue grew 3% over the previous quarter."* Which company? Which quarter? The chunk lost its context.

Fix: before embedding, **prepend a short context** to each chunk:
- Simple version: prepend the **title + section breadcrumb**: `"Doc: ACME 10-Q Q2 2025 > Financial results\n" + chunk`.
- LLM version (Anthropic's *Contextual Retrieval*): ask an LLM, with the whole document, to write 1–2 sentences that situate the chunk; prepend it; then build **both** embeddings and BM25 on the contextualized chunk. With prompt caching, the cost of sending the same document many times is small.

Anthropic reported this cut retrieval failures a lot (around half with contextual embeddings + contextual BM25, and more when reranking was added). Exact numbers depend on data, the direction is very consistent.

### 5.8 Late chunking (advanced)
Embed the **whole long document** with a long-context embedding model first, then pool the token vectors per chunk.
Each chunk vector "knows" the surrounding text. Needs a model that exposes token embeddings. Good to know for interviews.

### 5.9 Proposition / LLM chunking
Ask an LLM to rewrite the document into small standalone facts ("propositions"). Very precise, very expensive. Use for small, high-value corpora.

### 5.10 Special content
- **Tables:** keep a table whole if small; if big, split by rows but **repeat the header row** in every piece; add an LLM summary chunk ("This table lists 2026 prices per plan").
- **Code:** split by function/class (`RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)`).
- **Q&A / FAQ:** one Q+A pair = one chunk.

### Which one should I use? (decision table)

| Situation | Choose |
|---|---|
| First version, any text | Recursive, 500 tokens, 10% overlap |
| Docs with headings (Markdown, HTML, manuals) | Structure-aware + heading breadcrumb |
| Answers need surrounding context | Parent-child or sentence-window |
| Chunks lose their subject ("it", "the company") | Contextual headers / contextual retrieval |
| Unstructured transcripts | Semantic chunking |
| Tables / code / FAQ | Special handling as above |

---

## 6. Multi-representation indexing (index one thing, return another)

The thing you **search** doesn't have to be the thing you **send to the LLM**.

| Index this… | …return this | Why |
|---|---|---|
| A summary of a section | The full section | Summaries match broad questions better |
| Hypothetical questions the chunk answers ("How many leave days do I get?") | The chunk | Question-to-question similarity is higher than question-to-answer |
| Table description | The full table | Tables embed badly |
| Image caption | The image (for a vision LLM) | Images aren't text-searchable |

LangChain: `MultiVectorRetriever`.

---

## 7. Keeping the index fresh (updates, deletes)

- Give every document a stable `doc_id` and store a **hash** of its content.
- On re-sync: hash changed → delete old chunks with that `doc_id`, insert new ones. Hash same → skip (saves embedding cost).
- Deleted at source → delete from index (otherwise the bot keeps quoting a removed policy). LangChain's **indexing API** (`index()` with a `RecordManager`) does exactly this.
- **Changing the embedding model = re-embed everything.** Vectors from two models are not comparable. Plan for it (store raw text; use index aliases to switch with zero downtime).

---

## Revision notes
- Garbage in, garbage out: **parse well, clean, de-dupe, look at your chunks**.
- Metadata = citations + filters + **access control** + freshness + updates (`doc_id`, `allowed_groups`, `updated_at`).
- Chunk size is a trade-off: small = precise but context lost; big = context but noisy. Start ~500 tokens, 10–15% overlap, then measure.
- Strategies: fixed → **recursive (default)** → **structure-aware** → semantic → **parent-child** / sentence-window → **contextual retrieval** → late chunking → propositions.
- Tables: keep header, summarise. Code: split by function. FAQ: 1 pair per chunk.
- **Index one thing, return another** (summaries, hypothetical questions, captions).
- Keep the index fresh with `doc_id` + hash; new embedding model = full re-index.

---
✅ **Done with 26.** Next: [27 Embeddings & vector search →](27_embeddings_and_vector_search.md)
