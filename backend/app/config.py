"""Configuration. Keys come only from environment variables, never from code."""
import os


def _env(name, default=""):
    return os.getenv(name, default)


MOCK_MODE = _env("GNANI_MOCK_MODE", "true").lower() == "true"
GNANI_API_KEY = _env("GNANI_API_KEY", "")
GNANI_BASE_URL = _env("GNANI_BASE_URL", "https://api.vachana.ai")
# STT REST in gnani-vachana 0.8.2 accepts ONE BCP-47 code only.
# Hinglish (Hindi + English mix) works best starting from hi-IN.
GNANI_STT_LANGUAGE = _env("GNANI_STT_LANGUAGE", "hi-IN")
GNANI_TTS_VOICE = _env("GNANI_TTS_VOICE", "Pranav")
GNANI_TTS_MODEL = _env("GNANI_TTS_MODEL", "timbre-v2.5")
GNANI_TTS_LANGUAGE = _env("GNANI_TTS_LANGUAGE", "") or None
DATABASE_PATH = _env("DATABASE_PATH", "./orders.db")
