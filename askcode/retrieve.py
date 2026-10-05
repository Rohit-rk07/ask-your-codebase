"""Dependency-free BM25 retriever. Identifier-aware tokenizer (splits snake_case / camelCase)
so questions like "where is the retry logic" match `retryWithBackoff`.
Swap in embeddings by implementing the same `search(query, k)` interface."""
import math, re
from collections import Counter

_word = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_camel = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")
STOP = {"the", "a", "an", "is", "of", "to", "in", "and", "or", "how", "does", "do", "what", "where", "for", "this", "it"}


def tokenize(text: str):
    toks = []
    for w in _word.findall(text):
        parts = [p.lower() for p in _camel.findall(w)]
        toks += parts + ([w.lower()] if len(parts) > 1 else [])
    return [t for t in toks if t not in STOP and len(t) > 1]


class BM25:
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        # index file path too so "where is auth" can hit auth.py
        self.docs = [Counter(tokenize(c["file"] + " " + c["text"])) for c in chunks]
        self.lens = [sum(d.values()) for d in self.docs]
        self.avg = sum(self.lens) / max(len(self.lens), 1)
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, k: int = 5):
        q = tokenize(query)
        scored = []
        for i, d in enumerate(self.docs):
            s = 0.0
            for t in q:
                if t in d:
                    tf = d[t]
                    s += self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg))
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        return [dict(self.chunks[i], score=round(s, 3)) for s, i in scored[:k]]
