import os
import httpx

CARTESIA_URL = "https://api.cartesia.ai/tts/bytes"
CARTESIA_VERSION = "2024-11-13"
MODEL_ID = "sonic-3"
VOICE_LEO = "0834f3df-e650-4766-a20c-5a93a43aa6e3"

# Map question index to emotion for variety
EMOTIONS = ["neutral", "curious", "content", "neutral", "content", "curious"]


def get_emotion_for_index(index: int) -> str:
    return EMOTIONS[index % len(EMOTIONS)]


def text_to_speech(text: str, emotion: str | None = None) -> bytes:
    """Generate TTS audio as MP3 bytes using Cartesia Sonic-3."""
    key = os.environ.get("CARTESIA_API_KEY")
    if not key:
        raise ValueError("CARTESIA_API_KEY not set")
    emotion = emotion or "neutral"
    payload = {
        "model_id": MODEL_ID,
        "transcript": text,
        "voice": {"mode": "id", "id": VOICE_LEO},
        "output_format": {"container": "mp3", "bit_rate": 128000, "sample_rate": 44100},
        "language": "en",
        "generation_config": {"volume": 1, "speed": 1, "emotion": emotion},
    }
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            CARTESIA_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {key}",
                "Cartesia-Version": CARTESIA_VERSION,
                "Content-Type": "application/json",
            },
        )
        r.raise_for_status()
        return r.content
