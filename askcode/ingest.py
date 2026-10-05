"""Clone (or open) a repo and split source files into overlapping line-based chunks."""
import pathlib, subprocess, tempfile

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", ".next", "target"}
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".php", ".c", ".h", ".cpp",
            ".cs", ".kt", ".swift", ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".json", ".html", ".css", ".sh"}
MAX_BYTES = 200_000


def clone(url: str) -> pathlib.Path:
    dest = pathlib.Path(tempfile.mkdtemp(prefix="askcode_"))
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)], check=True)
    return dest


def iter_files(root: pathlib.Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXT and not (set(p.parts) & SKIP_DIRS):
            if p.stat().st_size <= MAX_BYTES:
                yield p


def chunk_file(path: pathlib.Path, root: pathlib.Path, size: int = 40, overlap: int = 8):
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    step = size - overlap
    for start in range(0, max(len(lines), 1), step):
        body = "\n".join(lines[start:start + size])
        if body.strip():
            yield {"file": str(path.relative_to(root)), "start": start + 1,
                   "end": min(start + size, len(lines)), "text": body}
        if start + size >= len(lines):
            break


def build_chunks(root) -> list:
    root = pathlib.Path(root)
    return [c for f in iter_files(root) for c in chunk_file(f, root)]
