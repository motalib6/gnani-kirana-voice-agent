# Cost notes — honest, no invented prices

## What is known

- The challenge gives each registration **5,000 programme credits**.
  The dashboard at app.gnani.ai/voice shows usage against those credits.
- Gnani does not publish a per-call / per-minute price in the docs
  checked for this project, so this file does NOT invent one.

## How to report cost (do this after your real-key test)

| Test | Calls (STT + TTS) | Audio length | Credits shown used | Credits left |
|------|-------------------|--------------|--------------------|--------------|
| 1 quiet order | | | | |
| 1 noisy order | | | | |
| 1 TTS confirmation | | | | |
| Demo recording (all takes) | | | | |
| **Total** | | | | |

## How to keep cost low in the demo

- Test the parser, dashboard, and pipeline in mock mode first (0 credits).
- Use short orders for real tests (5-10 seconds, not long conversations).
- Record the demo video in as few takes as possible, and reuse one
  successful real call in the video instead of re-running it live many times.
- If credits run low, switch back to mock mode for UI work and save
  real calls for the final eval table only.

## Cost per successful order (fill after testing)

- Successful real orders tested: ___
- Total credits used for those orders: ___
- Credits per successful order: ___ (total / successful orders)

Do not put a rupee price in the submission unless the dashboard or
Gnani's own pricing page states it. "Credits per order" from your own
dashboard is a defensible number; a guessed rupee price is not.
