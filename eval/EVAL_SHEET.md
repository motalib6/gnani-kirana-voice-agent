# Evaluation sheet — fill honestly, including failures

Copy this table into your README / submission. Judges trust a table with
failures more than a claim of "100% accuracy".

| # | Case | Audio type | Spoken (Hinglish) | Expected order | Gnani transcript | Got it right? | Latency | Notes |
|---|------|------------|-------------------|----------------|------------------|---------------|---------|-------|
| 1 | Happy path | Clean mic | 2 kg atta, 1 litre tel | atta 2kg, tel 1L, Rs 240 | | | | |
| 2 | Happy path | Clean mic | 1 kg chini | chini 1kg, Rs 42 | | | | |
| 3 | Hindi number | Clean mic | do kg chawal | chawal 2kg, Rs 120 | | | | |
| 4 | Missing qty | Clean mic | atta chahiye | Ask quantity, do not assume silently | | | | |
| 5 | Unknown item | Clean mic | 5 kg gold chahiye | Clarify / handoff, NO price | | | | |
| 6 | Code-switch | Clean mic | 2 kg atta and 1 litre oil please | atta 2kg, tel 1L | | | | |
| 7 | Noisy | Fan / traffic bg | 2 kg atta, 1 litre tel | Same as #1 | | | | |
| 8 | Phone-like | 8kHz / low volume | 2 kg atta, 1 litre tel | Same as #1 | | | | |
| 9 | Fast speech | Clean mic | 3 kg dal aur 2 kg namak jaldi | dal 3kg, namak 2kg | | | | |
| 10 | Correction | Clean mic | 2 kg atta — nahi, 3 kg atta | atta 3kg only | | | | |
| 11-20 | Your own | Mix | Add shopkeeper + customer tests | | | | | |

Also record, once, for the whole demo run:
- Total Gnani credits used: ___ / 5000
- STT average latency (if the dashboard shows it): ___
- TTS first-audio time (if shown): ___
- Cost per successful order in credits: ___

Rules: use synthetic shop data and your own voice / consenting testers only.
No real customer calls, no real phone numbers in recordings or screenshots.
