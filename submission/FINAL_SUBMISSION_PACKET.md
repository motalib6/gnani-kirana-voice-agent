# Final submission packet — Bolkar Order Karo (ready to copy into the Gnani form)

Deadline: 10 November 2026, 11:59 PM IST. No extensions.
Official steps: 1 Register, 2 Build, 3 Post your demo, 4 Submit.
Tagging alone does not complete the entry — you must nominate the post in Step 4.

## Step 1 — Registration (fill exactly as in your Gnani account)

- Full name: Sk Motalib
- Email / phone / college / degree / discipline / year of study /
  graduation year / city: use exactly what you registered with on
  app.gnani.ai. Do not change these in the form to match a guess.
- Team: Solo (no teammate)

## Step 2 — Build details (copy these)

Project title:
Bolkar Order Karo — Kirana Hinglish Voice Order Agent

Problem you are solving:
Small kirana customers order by phone, and shopkeepers write orders on
paper. English typing apps exclude customers who prefer speaking
Hinglish, and orders are missed after shop hours. Noisy phone audio
makes normal chatbots fail on exactly the calls that matter.

Who will use it:
Kirana customers who want to order by speaking Hinglish, and small
shopkeepers who want orders in one dashboard, with one-tap accept.

Gnani AI models / APIs used:
- Gnani speech-to-text, language hi-IN, via gnani-vachana (app.gnani.ai/voice)
- Timbre v2.5 text-to-speech, voice Pranav
- NOT claimed: Evon API (not on the API platform for this challenge),
  agent builder (out of scope for this challenge)

How it works:
Customer speaks Hinglish -> Gnani STT transcribes it -> the agent
matches items only against the shop price list and calculates the
total -> Gnani Timbre TTS speaks the confirmation back -> the order is
saved for the shopkeeper to accept. Unknown items are never priced by
guesswork; the agent asks a clarification question or hands off to the
shopkeeper. The browser recording is converted to WAV before upload,
because Gnani does not accept webm. Devanagari transcripts are
transliterated before parsing, so "एक के जी आटा" becomes 1 kg atta.

Each member's contribution:
Solo build by Sk Motalib — backend, Gnani STT/TTS integration, Hinglish
parser including Devanagari handling, shop-only search, shopkeeper
dashboard, frontend, evaluation, and demo video.

GitHub repository:
https://github.com/motalib6/gnani-kirana-voice-agent

## Step 3 — Demo post (already published)

LinkedIn post (nominated post link):
https://lnkd.in/p/dngANpeV
Also save the full linkedin.com/posts/... link from the post itself and
use that in the form if the form prefers a full URL.
Hashtags on the post: #GnaniAI #GreatIndianAIInternshipChallenge
#VoiceAI #Hinglish #AIForIndia #SovereignAI
Before submitting, confirm on LinkedIn itself: video is attached and
plays, @Gnani AI is a blue clickable mention, and the post is Public.
Do not delete the post or remove hashtags/mention after submitting.

Optional X post (not required if LinkedIn is nominated):
Use the same video and the same hashtags, tag Gnani AI, and nominate
that X link as a second platform only if you actually post it.

## Step 4 — Submit (what the form asks for)

- Demo video: upload / link the video you already posted on LinkedIn.
- Written project explanation: use the Problem + How it works text above.
- Gnani models/APIs used: use the list above.
- One nominated post link per platform: LinkedIn link above (and X link
  only if you posted on X).

## Results — verified, not invented

- Parser evaluation: 20/20 pass (eval/eval.py, eval/eval_results.csv)
- Real voice test: Gnani STT + TTS worked in real mode on Windows,
  including a Devanagari transcript "एक के जी आटा" -> 1 kg atta, Rs 45,
  after the Devanagari parser fix.
- Demo order example: 2 kg atta + 1 litre tel = Rs 240.
- Credits used: FILL FROM YOUR GNANI DASHBOARD BEFORE SUBMITTING.
  Do not guess this number. Write the dashboard figure here:
  Credits used: ___ / 5000
- Biggest failures found and fixed (honest, judges like this):
  1. backend/.env was silently ignored — fixed by loading backend/.env
     with python-dotenv.
  2. Browser webm was mislabelled as wav, then rejected by Gnani —
     fixed by converting the recording to WAV in the browser.
  3. Devanagari transcripts scored 0 items — fixed by transliterating
     Devanagari to Roman before parsing.

## After submitting — user-only steps

1. Screenshot the form confirmation and save it.
2. Check email for a submission confirmation.
3. Keep the LinkedIn post live. Do not buy engagement, use bots, or do
   engagement swaps — verified engagement decides the shortlist, and
   bought engagement can disqualify the entry.
4. Interview prep (after submissions close, before 1 Jan 2027 start):
   be ready to demo the app live, explain the STT -> parser -> total ->
   TTS -> dashboard flow, the WAV conversion, the Devanagari fix, the
   .env fix, and why unknown items get Rs 0 instead of a guessed price.
