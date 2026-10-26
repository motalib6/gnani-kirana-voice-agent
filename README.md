# Bolkar Order Karo — Kirana Hinglish Voice Order Agent

**Built for: The Great Indian AI Internship Challenge, Gnani.ai**
**Deadline: 10 November 2026, 11:59 PM IST — one entry only**
**Gnani technology used: Prisma v2.5 Speech-to-Text + Timbre v2.5 Text-to-Speech via app.gnani.ai / docs.gnani.ai**

> Synthetic demo data only. No real phone numbers, Aadhaar, PAN, bank details
> or real customer calls are used in this project or its demo.
>
> **Working status (26 Oct 2026, tested here):** parser eval 20/20 PASS,
> live FastAPI server tested (health, products, text-order Rs 240,
> RAG search, order save + accept, WebSocket voice pipeline with
> confirmation). Real Gnani STT/TTS code is fully wired to
> gnani-vachana 0.8.2 — it needs YOUR key in backend/.env to run in
> real mode, and that step is for you to test (see TESTING.md section 4).
> Mock mode needs no key.

## 1. Problem

A small kirana customer usually orders by phone or by visiting the shop.
Typing an order in English in an app is slow, and after shop hours orders
are missed. Shopkeepers also repeat the same work: listen, write the items
down, remember prices, add the total, and confirm it back.

This agent lets a customer speak in Hinglish, for example:

> "Bhaiya, 2 kg atta, 1 litre tel, aur 1 kg chini chahiye, kal subah de dena."

The agent transcribes it, matches it against the shop price list, calculates
the total, speaks the confirmation back in Hinglish, and saves the order for
the shopkeeper to accept in one tap.

## 2. Who uses it

- **Customer:** speaks Hinglish on a phone or browser, no English typing needed.
- **Shopkeeper:** sees new orders on a simple dashboard, accepts or rejects
  with one tap, and does not need to write orders on paper.
- **Gnani / judges:** get a real, measurable voice pipeline, not just a chat UI.

## 3. Architecture

```
Customer voice (mic / phone-like audio)
        |
        v
Gnani Prisma v2.5 STT  (hi-IN + en-IN code-switching)
        |
        v
Order parser + price-list lookup (RAG-style: only shop data, no hallucinated prices)
        |
        +--> Unknown item / missing quantity?  Ask a short clarification question
        |
        v
Order total + confirmation text (Hinglish)
        |
        +--> Gnani Timbre v2.5 TTS speaks the confirmation back
        |
        v
SQLite order store + shopkeeper dashboard (React-ready HTML in this skeleton)
        |
        v
Human handoff: shopkeeper accepts, or customer is told "dukandar se confirm karke batate hain"
```

Key AI Engineer decisions, not just a demo:

1. **No invented prices.** If an item is not in `price_list.json`, the agent
   says so. It never guesses a price.
2. **Confirmation before saving.** A parsed order is only saved as a real
   order after the customer confirms, or the shopkeeper accepts it.
3. **Human handoff.** Low confidence, unknown items, or very large totals go
   to the shopkeeper instead of being auto-confirmed.
4. **Evaluation, not vibes.** See `eval/` for the 20-case test sheet:
   clean audio, noisy audio, phone-like audio, Hinglish code-switching,
   missing quantity, and unknown item cases.

## 4. Tech stack

- Backend: Python + FastAPI
- Voice: Gnani Prisma v2.5 (STT), Gnani Timbre v2.5 (TTS)
- Optional real-time upgrade: Pipecat or LiveKit plugin from Gnani docs
  (Gnani's own internship listing names LiveKit / Pipecat experience as
  good-to-have — this is the upgrade path after the REST skeleton works)
- Frontend: plain HTML/JS in this skeleton, so it runs anywhere.
  Replace it with React later without changing the backend API.
- Storage: SQLite (demo). Swap to Postgres for production.
- Language codes used: `hi-IN` and `en-IN` together for Hinglish.

## 5. Run it (mock mode first, no key needed)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Leave GNANI_MOCK_MODE=true for the first run
uvicorn app.main:app --reload --port 8000
```

Then open `frontend/index.html` in a browser, or visit:

- Health: http://127.0.0.1:8000/health
- Products: http://127.0.0.1:8000/api/products
- Orders: http://127.0.0.1:8000/api/orders

### Switch to real Gnani APIs

1. Register for the challenge and sign in at `app.gnani.ai/voice` with the
   same email you registered with.
2. Create API keys from the dashboard and put them in `backend/.env`.
   Never commit `.env` and never paste a key into a demo video, README,
   LinkedIn post, GitHub repo, or chat.
3. Set `GNANI_MOCK_MODE=false` and restart uvicorn.
4. The adapter in `backend/app/gnani_client.py` already calls the real
   clients (gnani-vachana 0.8.2: `GnaniSTTClient.transcribe_bytes` with
   `language_code="hi-IN"`, and `GnaniTTSClient.synthesize` with
   voice `Pranav`, model `timbre-v2.5`). A Gnani auth/credit failure
   returns a clear 502, never a fake transcript.
5. Note for the challenge: the agent builder is out of scope for this
   challenge, and Evon v3.3 is not on the API platform yet. This project
   therefore claims only Prisma STT + Timbre TTS, which are on the API
   platform. Do not claim Evon API use in the submission.
6. Full user testing steps, including noisy audio and cost recording,
   are in `TESTING.md` and `COST_NOTES.md`.

## 6. API (skeleton)

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Mock/real mode + product count |
| GET | `/api/products` | Synthetic shop price list |
| POST | `/api/text-order` | Parse typed Hinglish text, return order + confirmation text |
| POST | `/api/voice-order` | Upload audio, STT -> parse -> TTS (mock returns text if no key) |
| POST | `/api/orders` | Save a confirmed order |
| GET | `/api/orders` | List saved orders for the shopkeeper |
| POST | `/api/tts` | Text -> speech audio (real mode only, otherwise a clear note) |

Example text-order request:

```json
{
  "text": "2 kg atta aur 1 litre tel chahiye",
  "customer_name": "Demo Customer"
}
```

Example response (prices are from the synthetic list only):

```json
{
  "transcript": "2 kg atta aur 1 litre tel chahiye",
  "items": [
    {"item": "atta", "quantity": 2, "unit": "kg", "price_per_unit": 45, "line_total": 90},
    {"item": "tel", "quantity": 1, "unit": "litre", "price_per_unit": 150, "line_total": 150}
  ],
  "total": 240,
  "confirmation_text": "Aapka order: 2 kg atta, 1 litre tel. Total 240 rupaye. Confirm karne ke liye haan bolo.",
  "needs_clarification": false
}
```

## 7. 15-day plan (26 Oct -> 10 Nov 2026)

- **Day 1-2:** Register, get keys, run this skeleton in mock mode, then one
  real STT + one real TTS call.
- **Day 3-5:** Real voice pipeline, mic recording, interruption handling,
  short clarification questions.
- **Day 6-8:** Price-list lookup, order save, shopkeeper dashboard, human
  handoff for unknown items.
- **Day 9-10:** 20-case evaluation: clean, noisy, phone-like, Hinglish,
  missing quantity, unknown item. Fill `eval/EVAL_SHEET.md` honestly,
  including failures.
- **Day 11-12:** 60-second demo video (see `demo/DEMO_SCRIPT_60SEC.md`),
  post on LinkedIn/X with #GnaniAI #GreatIndianAIInternshipChallenge.
- **Day 13-14:** Polish README, record each member's contribution clearly,
  final submission before 11:59 PM IST on 10 Nov. Keep one buffer day.

## 8. Award angles (honest mapping, not a guarantee)

- **Mixed Vibes:** Hinglish code-mixed voice experience.
- **Real Deal:** kirana customer + shopkeeper, a real everyday problem.
- **Noise Canceller:** tested on noisy / phone-like audio, with results shown.
- **Small Town, Big Build:** built from Jajpur, Odisha (Tier 2/3 story).
- **Solo Ninja:** if built solo, say so clearly with one person's contribution.

## 9. What to show judges in 60 seconds

1. Speak a Hinglish order (10 sec).
2. Show transcript + matched items + total (15 sec).
3. Play the Hinglish voice confirmation (10 sec).
4. Show the order appearing on the shopkeeper dashboard (10 sec).
5. Show one noisy-audio test + one failure/handoff case (15 sec).

That last 15 seconds is what separates this from a normal chatbot demo.
Every other entry shows the happy path. This one shows the hard path too.

## 10. Submission checklist

- [ ] Working app, not screenshots only
- [ ] Gnani models named: Prisma v2.5 STT, Timbre v2.5 TTS
- [ ] Demo video posted on LinkedIn/X before submission, Gnani tagged
- [ ] One nominated post link per platform in the submission form
- [ ] Written explanation + each member's contribution
- [ ] No real personal data, no bought engagement, no bots
- [ ] Submitted before 10 Nov 2026, 11:59 PM IST
