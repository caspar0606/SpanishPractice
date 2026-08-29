"""OpenAI text-to-speech, with a file cache so the same line is not billed twice."""

from src.infrastructure.audio import cache as audio_cache
from src.infrastructure.config.config import OPENAI_API_KEY


class OpenAiTtsGateway:
    def synthesise(self, text: str, voice: str = "nova") -> str:
        cleaned = (text or "").strip()
        if not cleaned:
            raise ValueError("Nothing to read aloud")
        clip_id = audio_cache.clip_id_for(cleaned, voice)
        if audio_cache.get(clip_id) is not None:
            return clip_id
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set, so audio cannot be generated")
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=cleaned,
        )
        audio_cache.put(clip_id, response.content)
        return clip_id
