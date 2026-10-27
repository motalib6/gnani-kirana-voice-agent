# Windows troubleshooting — Gnani Kirana Voice Agent

You do not need to describe the error in words. Run one script and paste its output.

## Fastest path: run the check script

1. Open PowerShell in the repo root (`gnani-kirana-voice-agent` folder).
2. If PowerShell blocks scripts, run this once in that window first:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
3. Run:
   `.\WINDOWS_CHECK.ps1`
4. Copy the whole output and send it to the assistant. **Do not add your API key** — the script never prints it, it only says whether a key looks set or empty.

What the script checks, in order: repo folder, Python, uvicorn, port 8000 listening,
`/health` (including `mock_mode`), `/api/products`, a mock text order
(`2 kg atta aur 1 litre tel` should total Rs 240), and `.env` presence only.

## If the script itself cannot run

- "WINDOWS_CHECK.ps1 is not recognised": you are not in the repo root. `cd` to the
  `gnani-kirana-voice-agent` folder first, then run `.\WINDOWS_CHECK.ps1`.
- "running scripts is disabled": use the `Set-ExecutionPolicy -Scope Process` line above, then re-run.

## Common results, and what they mean

| Script says | It means |
|---|---|
| Port 8000 NOT LISTENING | The server window was closed, or never started. In `backend`, run `uvicorn app.main:app --reload --port 8000` and keep that window open. |
| Health FAILED, port listening | Server started but the app crashed on startup — paste the PowerShell window's error lines too. |
| Mock order total is not Rs 240 | Parser problem — paste the script output; do not re-clone yet. |
| `.env` mock mode OFF + API key EMPTY/placeholder | Real mode cannot work yet. Put the real key in `backend\.env` only (never in chat), restart the server, re-run the script. |
| Real voice order gives 502 | That is the designed Gnani failure path, not a fake transcript. Paste the 502 message (not the key) — it usually means key, credits, or audio format. |
| `python3 not found` / `source not recognized` | Not errors in this project on Windows. Use `python` (not `python3`) and skip `source`; system Python already worked in the 26 Oct test. |

## Do not do

- Do not paste your Gnani key in chat, in a screenshot of `.env`, or in a video.
- Do not run `git remote add` / `git push -u origin main` again — the repo is already pushed.
- Do not re-clone to "fix" an error before sending the script output; re-cloning wipes local `.env` work.
