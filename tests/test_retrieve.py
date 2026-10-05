import pathlib, tempfile
from askcode.ingest import build_chunks
from askcode.retrieve import BM25, tokenize


def make_repo():
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "net.py").write_text("def retryWithBackoff(fn):\n    for attempt in range(5):\n        sleep(2 ** attempt)\n")
    (d / "auth.py").write_text("def login(user, password):\n    return hash_password(password) == user.hash\n")
    (d / "node_modules").mkdir(); (d / "node_modules" / "x.js").write_text("retry retry retry")
    return d


def test_tokenize_splits_identifiers():
    assert {"retry", "with", "backoff"} <= set(tokenize("retryWithBackoff"))
    assert "hash" in tokenize("hash_password")


def test_search_finds_right_file_and_skips_vendor():
    chunks = build_chunks(make_repo())
    assert all("node_modules" not in c["file"] for c in chunks)
    hits = BM25(chunks).search("where is the retry logic with backoff?")
    assert hits[0]["file"] == "net.py"
    assert BM25(chunks).search("how does password login work")[0]["file"] == "auth.py"
