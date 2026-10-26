"""Run 20 parser test cases and write eval_results.csv.

Usage (from backend/ with the venv active, or from the repo root with
PYTHONPATH=backend):  python eval/eval.py

Cases cover: happy path, Hindi numbers, missing quantity, unknown item
(must be Rs 0, never invented), code-switching, noisy-STT mishearings
(aata, chaval, daal, cheeni, tail), correction-style re-orders, and
multi-item orders. Voice (real Gnani) results go in EVAL_SHEET.md by hand
— this file tests the parser that sits behind the voice pipeline.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app import agent  # noqa: E402

# (spoken / transcript text, expected total in Rs)
CASES = [
    ("2 kg atta aur 1 litre tel chahiye", 240),
    ("1 kg chini", 42),
    ("do kg chawal", 120),
    ("atta chahiye", 45),
    ("5 kg gold chahiye", 0),
    ("teen kg dal aur 2 kg namak", 380),
    ("1 litre tel", 150),
    ("2 kg chawal aur 1 kg dal", 230),
    ("paanch kg atta", 225),
    ("aadha kg chini", 21),
    ("2 kg aata chahiye", 90),          # noisy: aata -> atta
    ("2 kg chaval chahiye", 120),       # noisy: chaval -> chawal
    ("1 kg daal", 110),                 # noisy: daal -> dal
    ("1 kg cheeni", 42),                # noisy: cheeni -> chini
    ("1 litre tail chahiye", 150),      # noisy: tail -> tel
    ("2 kg atta and 1 litre oil please", 240),  # code-switch, oil=tel alias? see note
    ("ek kg namak aur ek sabun", 60),
    ("10 kg chawal", 600),
    ("3 kg atta, 2 kg chini, 1 litre tel", 369),
    ("kuch nahi chahiye", 0),
]

if __name__ == "__main__":
    price_list = agent.load_price_list()
    out = Path(__file__).parent / "eval_results.csv"
    passed = 0
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["input", "expected_total", "actual_total", "pass", "items"])
        for text, expected in CASES:
            parsed = agent.parse_order(text, price_list)
            ok = parsed["total"] == expected
            passed += ok
            writer.writerow([text, expected, parsed["total"], ok, parsed["items"]])
            print(f"{'PASS' if ok else 'FAIL'} | {text} | {parsed['total']} (expected {expected})")
    print(f"\n{passed}/{len(CASES)} passed. Wrote {out}")
    print("NOTE: case 16 uses 'oil' — tel aliases include 'oil', so it passes "
          "by design. If you remove that alias, update the expected total to 90.")
