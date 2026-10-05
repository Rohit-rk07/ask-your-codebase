# Ask Your Codebase

Ask natural-language questions about any GitHub repo and get answers **cited to file and line range**.

**Pipeline:** clone → chunk (40 lines, 8 overlap) → BM25 index with identifier-aware tokenizing → top-k → Claude answers using only the retrieved snippets.

```bash
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=sk-...        # optional; without it you get the raw top matches
askcode https://github.com/pallets/flask "how are blueprints registered?"
askcode ./local/path                    # interactive mode
```

## Design notes
- Zero required dependencies: retrieval is pure-Python BM25 (works offline, fast, great for code identifiers).
- `BM25.search(query, k)` is the only retriever interface — drop in an embedding/vector store (e.g. sentence-transformers + FAISS) for hybrid search.
- The prompt forces citations and "I don't know" when context is missing, to reduce hallucination.

## Roadmap
Hybrid BM25 + embeddings, AST-aware chunking (functions/classes), persistent index cache, web UI, eval set of Q&A pairs.
