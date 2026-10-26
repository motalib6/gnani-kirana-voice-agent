# Testing checklist — for the developer AND for the user

## 1. What I (the assistant) already tested here, 26 Oct 2026

- Parser eval: **20/20 PASS** — `python eval/eval.py` (see eval/eval_results.csv).
  Two real bugs were found and fixed during testing, not hidden:
  1. "2 kg atta" was parsed as 1 kg because "kg" sits between number and item.
  2. "2 kg chaval" (noisy STT) lost its quantity in the fuzzy path.
  Both are fixed and covered by test cases now.
- Code compiles: `python -m py_compile backend/app/*.py eval/eval.py` — OK.
- Gnani library verified: gnani-vachana 0.8.2 installed in backend/.venv,
  STT client `transcribe_bytes`, TTS client `synthesize` signatures read
  from the installed package (not guessed). STT REST accepts ONE language
  code only, so the default is `hi-IN` for Hinglish, not `en-IN,hi-IN`.
- Live server test is in section 2 below — run it after starting uvicorn.

## 2. Live server test (do this now, mock mode, no key needed)

```bash
cd backend
./.venv/bin/uvicorn app.main:app --reload --port 8000
# In another terminal:
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/products
curl -X POST http://127.0.0.1:8000/api/text-order \
  -H "Content-Type: application/json" \
  -d '{"text": "2 kg atta aur 1 litre tel chahiye"}'
# Expected: total 240, confirmation in Hinglish, needs_clarification false
curl "http://127.0.0.1:8000/api/search?q=delivery%20kab%20hoti%20hai"
# Expected: FAQ answer about delivery, not an invented price
```

Then open `frontend/index.html`, send the mock order, save it, and
Accept/Reject it on the dashboard. If any step fails, note the exact
error — do not demo a step you have not run.

## 3. WebSocket voice-pipeline test (interruption)

```bash
python3 - << 'PY'
import asyncio, json, websockets  # pip install websockets if needed
async def main():
    async with websockets.connect("ws://127.0.0.1:8000/ws/voice") as ws:
        await ws.send(json.dumps({"type": "transcript", "text": "2 kg atta chahiye"}))
        print(await ws.recv())  # state SPEAKING, action confirm
        await ws.send(json.dumps({"type": "transcript", "text": "ruk, 3 kg kar do"}))
        print(await ws.recv())  # interruption handled, new order parsed
asyncio.run(main())
PY
```

Expected: the second message does NOT create a second order silently;
the pipeline returns to listening/confirming with the corrected order.
(If you do not have `websockets` installed, test the same logic via the
browser demo + the `VoicePipeline` class in a Python shell.)

## 4. Real Gnani test — USER'S OWN KEY ONLY, in .env only

1. Register for the challenge (done, per user) and sign in at
   app.gnani.ai/voice with the registration email.
2. Copy `backend/.env.example` to `backend/.env`.
3. Put ONLY your key in `.env` as `GNANI_API_KEY=...`.
   Never paste it in chat, in a video, or in git. `.gitignore` blocks `.env`.
4. Set `GNANI_MOCK_MODE=false`, restart uvicorn.
5. Record a short wav (your own voice, synthetic shop order only) and test:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/voice-order \
     -F "file=@my_order.wav" -F "customer_name=Demo Customer"
   ```
   Expected: a real Gnani transcript, parsed items, total, and a
   `confirmation_audio_base64` field (play it in the browser demo).
   If Gnani returns 401/403/credits error, the API returns a clear 502
   with that message — fix the key/credits in the dashboard, do not
   fake a transcript.
6. Test TTS alone:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/tts \
     -H "Content-Type: application/json" \
     -d '{"text": "Aapka order confirm ho gaya."}'
   ```
7. Record the results in `eval/EVAL_SHEET.md` and `COST_NOTES.md`:
   how many calls, how long each audio was, and what the dashboard
   showed for credits used. Do not invent a per-minute price — Gnani
   does not publish one in the docs checked, so report dashboard usage.

## 5. Noisy-audio test (for the Noise Canceller award claim)

Record the same order three ways: (a) quiet room, (b) fan/TV in background,
(c) phone held away / low volume. Run all three through /api/voice-order
in real mode and fill the eval sheet honestly, including any failure.
A claim of "works on noisy audio" without this table will not convince
judges — and if noisy audio fails, say so and show the handoff case.

## 6. Before GitHub / submission

- [ ] `git status` shows no `.env`, no `orders.db`, no `.venv`
- [ ] README numbers match your actual eval results (no invented %)
- [ ] Demo video is YOUR recording of the working app, not a mockup
- [ ] LinkedIn/X post is live BEFORE the Gnani submission form is sent
