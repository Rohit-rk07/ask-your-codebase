"""Generate a grounded answer with Claude; falls back to showing retrieved snippets."""
import os

SYSTEM = ("You answer questions about a codebase using ONLY the provided snippets. "
          "Cite sources as [file:start-end]. If the snippets don't contain the answer, say so.")


def format_context(hits):
    return "\n\n".join(f"[{h['file']}:{h['start']}-{h['end']}]\n{h['text']}" for h in hits)


def answer(question: str, hits, model: str = "claude-sonnet-4-5") -> str:
    if not hits:
        return "No relevant code found."
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return "(No ANTHROPIC_API_KEY set — showing top matches)\n\n" + format_context(hits)
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=model, max_tokens=800, system=SYSTEM,
        messages=[{"role": "user", "content": f"Snippets:\n{format_context(hits)}\n\nQuestion: {question}"}])
    return msg.content[0].text
