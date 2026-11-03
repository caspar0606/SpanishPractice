"""OpenAI Whisper transcription."""

import io

from src.infrastructure.config.config import OPENAI_API_KEY


class OpenAiSttGateway:
    def transcribe(self, audio_bytes: bytes, filename: str = "speech.webm") -> str:
        if not audio_bytes:
            raise ValueError("No audio was recorded")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set, so speech cannot be transcribed")
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        buffer = io.BytesIO(audio_bytes)
        buffer.name = filename
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language="es",
        )
        return (result.text or "").strip()
