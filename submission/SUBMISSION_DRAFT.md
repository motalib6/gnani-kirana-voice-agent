# Submission draft — copy, then edit with YOUR real numbers

## Project title

Bolkar Order Karo — Kirana Hinglish Voice Order Agent

## Problem

Small kirana customers order by phone, and shopkeepers write orders on paper.
English typing apps exclude customers who prefer speaking Hinglish, and
orders are missed after shop hours. Noisy phone audio makes normal
chatbots fail on exactly the calls that matter.

## Who will use it

- Kirana customers who want to order by speaking Hinglish.
- Small shopkeepers who want orders in one dashboard, with one-tap accept.
- Later: any small business that takes phone orders (pharmacy, restaurant).

## Gnani AI models / APIs used

- Prisma v2.5 — Speech-to-Text (Hinglish, en-IN + hi-IN)
- Timbre v2.5 — Text-to-Speech (Hinglish confirmation voice)
- Platform: app.gnani.ai/voice, docs: docs.gnani.ai
- NOT claimed: Evon API (not on the API platform for this challenge),
  agent builder (out of scope for this challenge).

## How it works (one paragraph for the form)

Customer speaks Hinglish -> Gnani Prisma STT transcribes it -> the agent
matches items only against the shop price list and calculates the total ->
Gnani Timbre TTS speaks the confirmation back -> the order is saved for the
shopkeeper to accept. Unknown items are never priced by guesswork; the agent
asks a clarification question or hands off to the shopkeeper.

## Each member's contribution

Solo build by Sk Motalib — backend, Gnani STT/TTS integration, order
parser, evaluation, frontend, dashboard, demo video.

## Nominated LinkedIn post (published 2026-10-29)

https://lnkd.in/p/dngANpeV
Hashtags: #GnaniAI #GreatIndianAIInternshipChallenge #VoiceAI
#Hinglish #AIForIndia #SovereignAI
Before submitting, confirm on LinkedIn: video attached and plays,
@Gnani AI is a blue mention, post is Public.

## Results (verified — credits still to fill from dashboard)

- Parser evaluation: 20/20 pass
- Real voice test: Gnani STT + TTS worked in real mode, including
  Devanagari "एक के जी आटा" -> 1 kg atta, Rs 45
- Demo order: 2 kg atta + 1 litre tel = Rs 240
- Credits used: ___ / 5000 (fill from Gnani dashboard, do NOT invent)
- Biggest failures fixed: .env ignored (dotenv fix), webm rejected
  (browser WAV conversion), Devanagari scored 0 (transliteration fix)

See FINAL_SUBMISSION_PACKET.md for the full field-by-field copy-paste
version for the Gnani form.

## LinkedIn / X post draft (edit, then post BEFORE submitting)

> I built Bolkar Order Karo for the Great Indian AI Internship Challenge.
>
> Bolkar order karo — speak in Hinglish, and a kirana order is understood,
> priced from the real shop list, confirmed by voice, and sent to the
> shopkeeper's dashboard.
>
> Built on Gnani AI's Prisma STT and Timbre TTS, and tested on noisy,
> phone-like audio — not just clean mic audio.
>
> Demo video below. Feedback welcome, especially from small shop owners.
>
> #GnaniAI #GreatIndianAIInternshipChallenge
>
> [Paste your demo video / link here. Tag Gnani AI in the post itself.]
