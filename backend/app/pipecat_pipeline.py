"""Optional real-time upgrade: Pipecat pipeline (NOT required to run the app).

Why this file is separate: the main app runs on FastAPI + the Gnani REST
clients with zero extra dependencies. If you want live interruption with
sub-second latency, add Pipecat and the official pipecat-gnani plugin:

    pip install pipecat-ai pipecat-gnani

Then, following the pipecat-gnani README (GnaniSTTService / GnaniTTSService
with a Gnani API key, plus an LLM service for reasoning), wire the same
states as voice_pipeline.py:

    transport (WebRTC) -> VAD -> Gnani STT -> LLM (order parser prompt,
      constrained to the price list) -> Gnani TTS -> transport

Rules the Pipecat version must keep, or the demo loses its edge:
  1. Interruption cancels TTS immediately (do not queue a stale confirmation).
  2. The LLM may only price items from price_list.json.
  3. Unknown items go to clarification / human handoff, never to a guess.
  4. Every turn is logged for the eval sheet (transcript, items, latency).

This file intentionally imports nothing at module level, so a missing
Pipecat install can never break the main FastAPI app.
"""
