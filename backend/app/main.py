"""FastAPI app for Bolkar Order Karo — fully working, mock or real Gnani.

Run (from backend/):
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env        # mock mode works with no key
    uvicorn app.main:app --reload --port 8000

Real Gnani test (user's own key, in .env only):
    GNANI_MOCK_MODE=false in .env, restart, then POST /api/voice-order
    with a real wav file. A Gnani auth/credit error is returned as a
    clear 502 message, never as a fake transcript.
"""
import base64
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import agent, config, order_store, rag, tools
from .gnani_client import GnaniClient
from .voice_pipeline import VoicePipeline

app = FastAPI(title="Bolkar Order Karo — Kirana Hinglish Voice Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

PRICE_LIST = agent.load_price_list()
KNOWLEDGE_BASE = rag.load_knowledge_base()
CLIENT = GnaniClient()
PIPELINE = VoicePipeline(PRICE_LIST)

# Linked frontend + backend: the repo root holds frontend/ and website/.
# So http://127.0.0.1:8000/ shows the app, no separate file to open.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_FILE = REPO_ROOT / "frontend" / "index.html"
WEBSITE_FILE = REPO_ROOT / "website" / "index.html"


@app.get("/", include_in_schema=False)
def root():
    """Serve the linked frontend app from the same origin as the API."""
    if FRONTEND_FILE.exists():
        return FileResponse(FRONTEND_FILE, media_type="text/html")
    return {"status": "ok", "message": "Frontend file not found. API is running — see /health."}


@app.get("/website", include_in_schema=False)
def website_demo():
    """Serve the classical website demo from the same origin."""
    if WEBSITE_FILE.exists():
        return FileResponse(WEBSITE_FILE, media_type="text/html")
    raise HTTPException(404, "Website demo file not found")


class TextOrderRequest(BaseModel):
    text: str
    customer_name: str = "Demo Customer"


class SaveOrderRequest(BaseModel):
    customer_name: str = "Demo Customer"
    items: list = []
    total: float = 0


class TTSRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mock_mode": config.MOCK_MODE,
        "shop": PRICE_LIST["shop_name"],
        "product_count": len(PRICE_LIST["products"]),
        "stt_language": config.GNANI_STT_LANGUAGE,
        "tts_voice": config.GNANI_TTS_VOICE,
    }


@app.get("/api/products")
def products():
    return PRICE_LIST


@app.get("/api/search")
def search(q: str):
    """RAG search: only shop products + shop FAQs, never invented prices."""
    return {"query": q, "results": rag.retrieve(q, PRICE_LIST, KNOWLEDGE_BASE)}


@app.post("/api/text-order")
def text_order(req: TextOrderRequest):
    parsed = agent.parse_order(req.text, PRICE_LIST)
    return {"transcript": req.text, **parsed}


@app.post("/api/voice-order")
async def voice_order(
    file: UploadFile = File(None),
    mock_text: str = Form(""),
    customer_name: str = Form("Demo Customer"),
):
    """Audio in -> Gnani STT -> parse -> Gnani TTS confirmation.

    Mock mode: send mock_text instead of real audio.
    Real mode: upload a wav/mp3 file; a Gnani failure returns 502.
    """
    audio_bytes = await file.read() if file is not None else b""
    if not config.MOCK_MODE and not audio_bytes:
        raise HTTPException(400, "Real mode needs an audio file upload.")
    # Gnani rejects webm outright (supported: ogg, wav, mp3, aac, m4a,
    # flac). The current frontend converts to WAV before upload, but an
    # old frontend sending webm should get a clear error, not a Gnani
    # ffmpeg dump.
    if not config.MOCK_MODE and file is not None:
        _ct = (file.content_type or "").lower()
        _fn = (file.filename or "").lower()
        if "webm" in _ct or _fn.endswith(".webm"):
            raise HTTPException(
                400,
                "Gnani does not support webm audio. Please pull the latest "
                "frontend, which converts the recording to WAV before upload, "
                "then record again.",
            )
    # AUDIO FORMAT FIX (was the real-mode STT bug): the browser records
    # webm/opus, but the old code always told Gnani the file was
    # "audio.wav", so Gnani's ffmpeg failed with "invalid start code in
    # RIFF header". Now the real uploaded filename / content type is
    # passed through, so Gnani converts the actual format.
    filename = "audio.webm"
    if file is not None:
        content_type = (file.content_type or "").lower()
        ext = None
        if "webm" in content_type:
            ext = ".webm"
        elif "mp4" in content_type or "m4a" in content_type:
            ext = ".m4a"
        elif "ogg" in content_type:
            ext = ".ogg"
        elif "wav" in content_type or "x-wav" in content_type:
            ext = ".wav"
        elif "mpeg" in content_type or "mp3" in content_type:
            ext = ".mp3"
        if ext:
            base = (file.filename or "audio").rsplit(".", 1)[0]
            filename = base + ext
        elif file.filename:
            filename = file.filename
    try:
        transcript = CLIENT.transcribe(audio_bytes, filename=filename, mock_text=mock_text)
    except Exception as exc:
        raise HTTPException(502, f"Gnani STT failed: {exc}") from exc
    parsed = agent.parse_order(transcript, PRICE_LIST)
    audio_b64 = None
    tts_error = None
    try:
        audio = CLIENT.speak(parsed["confirmation_text"])
        if audio:
            audio_b64 = base64.b64encode(audio).decode()
    except Exception as exc:
        tts_error = str(exc)
    result = {
        "transcript": transcript,
        "confirmation_audio_base64": audio_b64,
        "customer_name": customer_name,
        **parsed,
    }
    if tts_error:
        result["tts_error"] = tts_error
    return result


@app.post("/api/orders")
def save_order(req: SaveOrderRequest):
    order_id = order_store.save_order(req.customer_name, req.items, req.total)
    return {"order_id": order_id, "status": "pending"}


@app.get("/api/orders")
def orders():
    return {"orders": order_store.list_orders()}


@app.post("/api/orders/{order_id}/accept")
def accept_order(order_id: int):
    if not order_store.update_status(order_id, "accepted"):
        raise HTTPException(404, "Order not found")
    return {"order_id": order_id, "status": "accepted"}


@app.post("/api/orders/{order_id}/reject")
def reject_order(order_id: int):
    if not order_store.update_status(order_id, "rejected"):
        raise HTTPException(404, "Order not found")
    return {"order_id": order_id, "status": "rejected"}


@app.post("/api/tts")
def tts(req: TTSRequest):
    audio = CLIENT.speak(req.text)
    if audio is None:
        return {
            "audio_base64": None,
            "note": "Mock mode: no audio generated. Set GNANI_MOCK_MODE=false with a real key for TTS.",
        }
    return {"audio_base64": base64.b64encode(audio).decode()}


@app.websocket("/ws/voice")
async def ws_voice(websocket: WebSocket):
    """Text-transcript WebSocket driving the voice pipeline.

    Client sends JSON:
      {"type": "transcript", "text": "2 kg atta chahiye"}
      {"type": "interrupt"}
      {"type": "tts_finished"}
    Server replies with the pipeline response (state, action, order).
    This is the testable core of the real-time pipeline; the browser
    demo uses it, and a Pipecat/LiveKit upgrade must preserve its states.
    """
    await websocket.accept()
    pipeline = VoicePipeline(PRICE_LIST)
    try:
        while True:
            msg = await websocket.receive_json()
            kind = msg.get("type")
            if kind == "transcript":
                response = pipeline.on_user_speech(msg.get("text", ""))
                await websocket.send_json({"type": "response", **response})
            elif kind == "interrupt":
                await websocket.send_json({"type": "interrupted", **pipeline.interrupt()})
            elif kind == "tts_finished":
                await websocket.send_json({"type": "state", "state": pipeline.tts_finished()})
            else:
                await websocket.send_json({"type": "error", "message": f"Unknown message type: {kind}"})
    except WebSocketDisconnect:
        pass
