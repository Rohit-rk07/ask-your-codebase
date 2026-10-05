import argparse, pathlib
from .ingest import clone, build_chunks
from .retrieve import BM25
from .answer import answer


def main(argv=None):
    p = argparse.ArgumentParser(prog="askcode", description="Ask questions about a GitHub repo (RAG).")
    p.add_argument("repo", help="GitHub URL or local path")
    p.add_argument("question", nargs="?", help="omit for interactive mode")
    p.add_argument("-k", type=int, default=6)
    a = p.parse_args(argv)

    root = pathlib.Path(a.repo) if pathlib.Path(a.repo).exists() else clone(a.repo)
    chunks = build_chunks(root)
    print(f"Indexed {len(chunks)} chunks from {root}")
    index = BM25(chunks)

    def ask(q):
        print("\n" + answer(q, index.search(q, a.k)) + "\n")

    if a.question:
        ask(a.question)
    else:
        while (q := input("ask> ").strip()) not in ("", "exit", "quit"):
            ask(q)


if __name__ == "__main__":
    main()
