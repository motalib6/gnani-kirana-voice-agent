"""Hinglish order parser. Rule-based on purpose: no invented prices.

This is the demo parser. In the real build, replace or extend it with:
  1. Gnani STT transcript (already done in main.py)
  2. An LLM step that extracts items/quantities, but ONLY against the
     price list — if the LLM returns an item not in the list, drop it and
     ask for clarification instead of inventing a price.
  3. A confidence check: low-confidence transcripts go to human handoff.
"""
import difflib
import json
import re
from pathlib import Path

HINDI_NUMBERS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
    "chhe": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "aadha": 0.5, "dedh": 1.5, "half": 0.5,
}

# Common noisy-STT mishearings, mapped to the real alias before parsing.
# This is a small, auditable map — it never adds a new product.
MISHEARINGS = {
    "aata": "atta", "ata": "atta", "chaval": "chawal", "chawl": "chawal",
    "daal": "dal", "cheeni": "chini", "tail": "tel", "namk": "namak",
}


def load_price_list():
    path = Path(__file__).parent / "price_list.json"
    return json.loads(path.read_text())


def _parse_number(text, start):
    """Find the last number before `start`.

    The number and the item are usually separated by a unit, e.g.
    "2 kg atta" or "do kg chawal", so we take the last number token in
    the window, not only a number glued to the item name.
    """
    before = text[max(0, start - 25):start]
    tokens = re.findall(r"(\d+(?:\.\d+)?|\b[a-z]+\b)", before)
    for token in reversed(tokens):
        if token.replace(".", "", 1).isdigit():
            return float(token)
        if token in HINDI_NUMBERS:
            return float(HINDI_NUMBERS[token])
    return 1.0  # "atta chahiye" without quantity = 1 unit, clarified later


def _normalise(text):
    """Fix known mishearings, keeping digits so quantities survive."""
    words = re.findall(r"\d+(?:\.\d+)?|[a-z]+", text.lower())
    return [MISHEARINGS.get(w, w) for w in words]


def parse_order(text, price_list):
    """Return (items, unknown_words, needs_clarification, total)."""
    lowered = text.lower()
    # Apply known mishearings to the full text first, so exact matching
    # (with its quantity parsing) works for noisy transcripts too.
    for wrong, right in MISHEARINGS.items():
        lowered = re.sub(rf"\b{re.escape(wrong)}\b", right, lowered)
    products = price_list["products"]
    items = []
    # Exact matches first.
    for product in products:
        for alias in product["aliases"]:
            for match in re.finditer(rf"\b{re.escape(alias)}\b", lowered):
                qty = _parse_number(lowered, match.start())
                items.append({
                    "item": product["item"],
                    "quantity": qty,
                    "unit": product["unit"],
                    "price_per_unit": product["price_per_unit"],
                    "line_total": round(qty * product["price_per_unit"], 2),
                })
                break  # one match per product per order
    # Fuzzy fallback for noisy transcripts: e.g. "attaa", "chawal" misheard.
    # Only accept a close match (>=0.75) to a real alias, and only if that
    # product was not already matched exactly. Never invent a product.
    if len(items) < 2:
        all_aliases = {}
        for product in products:
            for alias in product["aliases"]:
                all_aliases[alias] = product
        words = _normalise(text)
        for idx, word in enumerate(words):
            if any(i["item"] in word or word in i["item"] for i in items):
                continue
            close = difflib.get_close_matches(word, list(all_aliases), n=1, cutoff=0.75)
            if not close:
                continue
            product = all_aliases[close[0]]
            if any(i["item"] == product["item"] for i in items):
                continue
            # Quantity: look at the words just before this word.
            before = " ".join(words[max(0, idx - 3):idx])
            qty = 1.0
            for token in reversed(before.split()):
                if token.replace(".", "", 1).isdigit():
                    qty = float(token)
                    break
                if token in HINDI_NUMBERS:
                    qty = float(HINDI_NUMBERS[token])
                    break
            items.append({
                "item": product["item"],
                "quantity": qty,
                "unit": product["unit"],
                "price_per_unit": product["price_per_unit"],
                "line_total": round(qty * product["price_per_unit"], 2),
            })

    total = round(sum(i["line_total"] for i in items), 2)
    needs_clarification = not items
    confirmation_parts = ", ".join(
        f"{_fmt_qty(i['quantity'])} {i['unit']} {i['item']}" for i in items
    )
    if items:
        confirmation = (
            f"Aapka order: {confirmation_parts}. "
            f"Total {total:g} rupaye. Confirm karne ke liye haan bolo."
        )
    else:
        confirmation = (
            "Sorry, main aapka order samajh nahi paya. "
            "Kripya item aur quantity dobara bolo, jaise '2 kg atta'."
        )
    return {
        "items": items,
        "total": total,
        "needs_clarification": needs_clarification,
        "confirmation_text": confirmation,
    }


def _fmt_qty(qty):
    return f"{qty:g}"
