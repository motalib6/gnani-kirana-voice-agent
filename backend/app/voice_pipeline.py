"""Voice conversation pipeline — listening, speaking, interruption.

This is a real, testable state machine, not a diagram. The browser demo
and the WebSocket endpoint both drive it:

  IDLE -> LISTENING (user starts speaking / sends transcript)
       -> THINKING (parse + price lookup)
       -> SPEAKING (confirmation is being played)
       -> CONFIRMING (waiting for haan / nahi)
       -> IDLE (order saved, or cancelled, or handed off)

Interruption: if the user speaks while the agent is SPEAKING, the
pipeline cancels the in-progress speech, keeps the partial order, and
goes back to LISTENING with the new transcript. That is the behaviour
real voice agents need — a user saying "ruk, 3 kg kar do" mid-confirmation
must not be ignored, and must not create a second order.

For a production real-time pipeline, the same states map onto Pipecat /
LiveKit: VAD detects speech, STT streams transcripts, TTS streams audio,
and an interrupt event cancels the TTS stream. See pipecat_pipeline.py
for that upgrade path. This file is the logic that upgrade must preserve.
"""
from . import agent


class VoicePipeline:
    def __init__(self, price_list):
        self.price_list = price_list
        self.state = "IDLE"
        self.current_order = None
        self.interrupted = False
        self.turns = []

    def start_listening(self):
        self.state = "LISTENING"
        self.interrupted = False
        return self.state

    def interrupt(self):
        """User spoke while the agent was speaking. Cancel speech."""
        was_speaking = self.state == "SPEAKING"
        self.interrupted = was_speaking
        if was_speaking:
            self.state = "LISTENING"
        return {"was_speaking": was_speaking, "state": self.state}

    def on_user_speech(self, transcript):
        """One full user turn. Returns the agent response dict."""
        # If we were speaking, this speech is an interruption first.
        interrupt_info = self.interrupt() if self.state == "SPEAKING" else {"was_speaking": False}
        self.state = "THINKING"
        self.turns.append({"role": "user", "text": transcript})

        lowered = transcript.lower()
        # Confirmation turn: only accept if we already have an order waiting.
        if self.current_order and any(
            w in lowered for w in ["haan", "confirm", "theek hai", "yes", "ok"]
        ) and not any(
            p["item"] in lowered for p in self.price_list["products"]
        ):
            self.state = "IDLE"
            order = self.current_order
            self.current_order = None
            response = {
                "state": self.state,
                "action": "confirmed",
                "order": order,
                "confirmation_text": "Order confirm ho gaya. Dhanyavaad!",
                "interrupted": interrupt_info["was_speaking"],
            }
            self.turns.append({"role": "agent", "text": response["confirmation_text"]})
            return response

        if any(w in lowered for w in ["nahi", "cancel", "radd"]):
            self.current_order = None
            self.state = "IDLE"
            response = {
                "state": self.state, "action": "cancelled",
                "confirmation_text": "Theek hai, order cancel kar diya.",
                "interrupted": interrupt_info["was_speaking"],
            }
            self.turns.append({"role": "agent", "text": response["confirmation_text"]})
            return response

        parsed = agent.parse_order(transcript, self.price_list)
        if parsed["needs_clarification"]:
            self.state = "LISTENING"
            action = "clarify"
        else:
            self.current_order = parsed
            self.state = "SPEAKING"
            action = "confirm"
        response = {
            "state": self.state, "action": action,
            "items": parsed["items"], "total": parsed["total"],
            "confirmation_text": parsed["confirmation_text"],
            "interrupted": interrupt_info["was_speaking"],
        }
        self.turns.append({"role": "agent", "text": response["confirmation_text"]})
        return response

    def tts_finished(self):
        if self.state == "SPEAKING":
            self.state = "CONFIRMING"
        return self.state
