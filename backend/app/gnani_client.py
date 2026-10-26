"""
Gnani adapter — the ONLY file that talks to Gnani. Fully wired, no stubs.

Library verified locally: gnani-vachana 0.8.2 (pip install gnani-vachana).
  from gnani.stt import GnaniSTTClient
  from gnani.tts import GnaniTTSClient
  STT:  GnaniSTTClient(api_key=...).transcribe_bytes(
            audio_bytes, filename="audio.wav", language_code="hi-IN")
        -> dict with a "transcript" key
  TTS:  GnaniTTSClient(api_key=...).synthesize(
            text, voice="Pranav", model="timbre-v2.5") -> bytes

MOCK MODE (default, GNANI_MOCK_MODE=true):
    transcribe() returns the transcript you pass in through `mock_text`,
    speak() returns None. The whole order flow works with no key.

REAL MODE (GNANI_MOCK_MODE=false):
    Put your challenge key in backend/.env as GNANI_API_KEY — never in
    chat, never in git, never in a demo video. The key comes from the
    dashboard at app.gnani.ai/voice for the email you registered with.
    If your dashboard key uses a different format than the single
    API-key format above, check docs.gnani.ai first and adjust only
    this file. The rest of the app only calls transcribe() and speak().
"""
from . import config


def _extract_transcript(result):
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        for key in ("transcript", "text", "transcription"):
            if result.get(key):
                return str(result[key])
        # Some responses nest the transcript one level down.
        for value in result.values():
            if isinstance(value, dict) and value.get("transcript"):
                return str(value["transcript"])
    return ""


class GnaniClient:
    def __init__(self, mock_mode=None):
        self.mock_mode = config.MOCK_MODE if mock_mode is None else mock_mode
        if not self.mock_mode and not config.GNANI_API_KEY:
            raise ValueError(
                "GNANI_MOCK_MODE=false but GNANI_API_KEY is missing. "
                "Set it in backend/.env or keep mock mode on."
            )

    def transcribe(self, audio_bytes, filename="audio.wav", mock_text=""):
        """Return a transcript string for audio bytes."""
        if self.mock_mode:
            if mock_text:
                return mock_text
            return "2 kg atta aur 1 litre tel chahiye"
        try:
            from gnani.stt import GnaniSTTClient
        except ImportError as exc:
            raise RuntimeError(
                "gnani-vachana is not installed. Run: pip install gnani-vachana"
            ) from exc
        client = GnaniSTTClient(
            api_key=config.GNANI_API_KEY, base_url=config.GNANI_BASE_URL
        )
        result = client.transcribe_bytes(
            audio_bytes, filename=filename,
            language_code=config.GNANI_STT_LANGUAGE,
        )
        transcript = _extract_transcript(result)
        if not transcript:
            raise RuntimeError(f"Gnani STT returned no transcript: {result!r}")
        return transcript

    def speak(self, text):
        """Return audio bytes for text, or None in mock mode."""
        if self.mock_mode:
            return None
        try:
            from gnani.tts import GnaniTTSClient
        except ImportError as exc:
            raise RuntimeError(
                "gnani-vachana is not installed. Run: pip install gnani-vachana"
            ) from exc
        client = GnaniTTSClient(
            api_key=config.GNANI_API_KEY, base_url=config.GNANI_BASE_URL
        )
        return client.synthesize(
            text, voice=config.GNANI_TTS_VOICE,
            model=config.GNANI_TTS_MODEL, language=config.GNANI_TTS_LANGUAGE,
        )
