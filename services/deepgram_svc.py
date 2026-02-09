import os
from deepgram import DeepgramClient

_client: DeepgramClient | None = None


def _client_get() -> DeepgramClient:
    global _client
    if _client is None:
        key = os.environ.get("DEEPGRAM_API_KEY")
        if not key:
            raise ValueError("DEEPGRAM_API_KEY not set")
        _client = DeepgramClient(api_key=key)
    return _client


def transcribe_audio(audio_bytes: bytes, content_type: str = "audio/webm") -> str:
    """Transcribe prerecorded audio. Returns transcript text."""
    client = _client_get()
    response = client.listen.v1.media.transcribe_file(
        request=audio_bytes,
        smart_format=True,
    )
    if not getattr(response, "results", None) or not response.results.channels:
        return ""
    channel = response.results.channels[0]
    if not channel.alternatives:
        return ""
    return (channel.alternatives[0].transcript or "").strip()
