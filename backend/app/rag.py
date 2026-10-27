"""Simple, deterministic retrieval over shop data — the RAG step.

No external embedding service is needed for this demo, so the retrieval
is fully testable offline: token overlap between the question and each
document (product or FAQ). The interface is deliberately small —
retrieve(query, price_list, knowledge_base, top_k) — so you can swap the
scorer for embeddings later without changing the agent or the API.

Rule that matters for judges: retrieval can only return shop data.
It can never invent a price. If nothing matches, the agent says so
instead of guessing.
"""
import json
import re
from pathlib import Path

from .agent import MISHEARINGS, transliterate_devanagari


def _tokens(text):
    return set(re.findall(r"[a-z]+", text.lower()))


def _query_tokens(query):
    """Normalise a search query the same way the parser does: Devanagari
    -> Roman, then known mishearings -> real alias. Without this, a
    Devanagari query scored 0 (tokens only match [a-z]+) and a noisy
    spelling like 'chaval' missed 'chawal', so search looked inaccurate
    even though the data was there."""
    transliterated = transliterate_devanagari(query)
    return {MISHEARINGS.get(t, t) for t in _tokens(transliterated)}


def load_knowledge_base():
    path = Path(__file__).parent / "knowledge_base.json"
    return json.loads(path.read_text())


def retrieve(query, price_list, knowledge_base, top_k=3):
    """Return up to top_k matching docs, each with a score."""
    q = _query_tokens(query)
    docs = []
    for product in price_list["products"]:
        text = " ".join([product["item"]] + product["aliases"])
        docs.append({
            "type": "product",
            "text": f"{product['item']}: Rs {product['price_per_unit']} per {product['unit']}",
            "score": len(q & _tokens(text)),
        })
    for faq in knowledge_base["faqs"]:
        text = faq["question"] + " " + " ".join(faq["tags"])
        docs.append({
            "type": "faq",
            "text": f"Q: {faq['question']} A: {faq['answer']}",
            "score": len(q & _tokens(text)),
        })
    docs = [d for d in docs if d["score"] > 0]
    docs.sort(key=lambda d: d["score"], reverse=True)
    return docs[:top_k]
