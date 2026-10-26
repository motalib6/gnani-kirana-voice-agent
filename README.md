# Bolkar Order Karo — Kirana Hinglish Voice Order Agent

> ### Speak, and the order is done.
> **A customer speaks in Hinglish. The agent understands the order, prices it from the real shop list, confirms it by voice, and sends it to the shopkeeper — no English typing, no paper notes, no missed calls.**

| | |
|---|---|
| Challenge | Great Indian AI Internship Challenge, Gnani.ai |
| Deadline | **10 November 2026, 11:59 PM IST — one entry only** |
| Gnani technology | Prisma v2.5 Speech-to-Text + Timbre v2.5 Text-to-Speech, via app.gnani.ai |
| Tested status | Parser evaluation **20 / 20 PASS** • Live server tested • WebSocket voice pipeline tested |
| Website demo | Open `website/index.html` — a classical shop-style landing page with a live order demo |

> Synthetic demo data only. No real phone numbers, Aadhaar, PAN, bank details,
> or real customer calls are used in this project or its demo.

## Try it in 30 seconds (no key, no install)

1. Open **`website/index.html`** in any browser.
2. Type this example order: `2 kg atta aur 1 litre tel chahiye`
3. You will see the total **₹240**, the Hinglish confirmation, and the shopkeeper flow.
4. Also try the noisy test (`2 kg aata`) and the unknown-item test (`5 kg gold`).
   The agent must **not** invent a price for gold.

## Why this is not just another chatbot

- **Hinglish first** — code-mixed speech, Hindi number words, and noisy, phone-like audio.
- **No invented prices** — prices come only from the shop price list. Anything else triggers a clarification question or a human handoff.
- **Voice confirmation** — Gnani TTS speaks the order back, so a wrong order is caught before it is saved.
- **A real user** — a kirana customer and a shopkeeper, not a toy demo.
- **Measured, not claimed** — an evaluation sheet, latency notes, and cost notes, instead of an unsupported accuracy claim.

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

- **Customer:** speaks Hinglish on a phone or browser, with no English typing needed.
- **Shopkeeper:** sees new orders on a simple dashboard, and accepts or rejects
  with one tap, with no need to write orders on paper.
- **Gnani / judges:** get a real, measurable voice pipeline, not just a chat interface.

## 3. Architecture

```
Customer voice (microphone / phone-like audio)
        |
        v
Gnani Prisma v2.5 STT  (language code hi-IN for Hinglish)
        |
        v
Order parser + price-list lookup (retrieval over shop data only,
no hallucinated prices)
        |
        +--> Unknown item / missing quantity?  Ask a short clarification question
        |
        v
Order total + confirmation text (Hinglish)
        |
        +--> Gnani Timbre v2.5 TTS speaks the confirmation back
        |
        v
SQLite order store + shopkeeper dashboard
        |
        v
Human handoff: the shopkeeper accepts, or the customer is told
the shopkeeper will confirm the order personally
```

Key AI engineering decisions, not just a demo:

1. **No invented prices.** If an item is not in `price_list.json`, the agent
   says so. It never guesses a price.
2. **Confirmation before saving.** A parsed order is only saved as a real
   order after the customer confirms, or the shopkeeper accepts it.
3. **Human handoff.** Low confidence, unknown items, or very large totals go
   to the shopkeeper instead of being auto-confirmed.
4. **Evaluation, not impressions.** See `eval/` for the 20-case test sheet:
   clean audio, noisy audio, phone-like audio, Hinglish code-switching,
   missing quantity, and unknown item cases.
5. **Interruption handling.** If the user speaks while the confirmation is
   playing, the pipeline cancels the old speech and processes the new
   instruction, instead of creating a second order silently.
   See `backend/app/voice_pipeline.py` and the WebSocket endpoint `/ws/voice`.

## 4. Tech stack

- Backend: Python + FastAPI
- Voice: Gnani Prisma v2.5 (STT), Gnani Timbre v2.5 (TTS)
- Retrieval: keyword retrieval over the shop price list and FAQ file
  (`backend/app/rag.py`). The interface is small, so embeddings can replace
  it later without changing the agent or the API.
- Optional real-time upgrade: Pipecat or LiveKit plugin from Gnani docs.
  Gnani's own internship listing names LiveKit / Pipecat experience as
  good-to-have. See `backend/app/pipecat_pipeline.py` for that upgrade path.
- Frontend: plain HTML/JavaScript in this project, so it runs anywhere.
  Replace it with React later without changing the backend API.
- Storage: SQLite (demo). Swap to Postgres for production.
- Language code: `hi-IN` for Hinglish STT in the gnani-vachana 0.8.2 client.
  That client accepts one STT language code only.

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

Full testing steps, including the live server test, the WebSocket test,
and the user's own real-key test, are in `TESTING.md`.

### Switch to real Gnani APIs

1. Register for the challenge and sign in at `app.gnani.ai/voice` with the
   same email you registered with.
2. Create API keys from the dashboard and put them in `backend/.env`.
   Never commit `.env` and never paste a key into a demo video, README,
   LinkedIn post, GitHub repository, or chat.
3. Set `GNANI_MOCK_MODE=false` and restart uvicorn.
4. The adapter in `backend/app/gnani_client.py` already calls the real
   clients (gnani-vachana 0.8.2: `GnaniSTTClient.transcribe_bytes` with
   `language_code="hi-IN"`, and `GnaniTTSClient.synthesize` with
   voice `Pranav`, model `timbre-v2.5`). A Gnani authentication or credit
   failure returns a clear 502 error, never a fake transcript.
5. Note for the challenge: the agent builder is out of scope for this
   challenge, and Evon v3.3 is not on the API platform yet. This project
   therefore claims only Prisma STT + Timbre TTS, which are on the API
   platform. Do not claim Evon API use in the submission.
6. Full user testing steps, including noisy audio and cost recording,
   are in `TESTING.md` and `COST_NOTES.md`.

## 6. API

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Mock/real mode + product count |
| GET | `/api/products` | Synthetic shop price list |
| GET | `/api/search` | Retrieval over shop products and FAQs only |
| POST | `/api/text-order` | Parse typed Hinglish text, return order + confirmation text |
| POST | `/api/voice-order` | Upload audio, STT -> parse -> TTS (mock returns text if no key) |
| POST | `/api/orders` | Save a confirmed order |
| GET | `/api/orders` | List saved orders for the shopkeeper |
| POST | `/api/orders/{id}/accept` | Shopkeeper accepts an order |
| POST | `/api/orders/{id}/reject` | Shopkeeper rejects an order |
| POST | `/api/tts` | Text -> speech audio (real mode only, otherwise a clear note) |
| WS | `/ws/voice` | Transcript / interruption / TTS-finished voice pipeline |

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

- **Day 1-2:** Register, get keys, run the app in mock mode, then one
  real STT + one real TTS call.
- **Day 3-5:** Real voice pipeline, microphone recording, interruption handling,
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
