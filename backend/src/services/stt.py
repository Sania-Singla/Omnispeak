from config import GROQ_CLIENT
from fastapi import UploadFile


class TranscriptionService:
    def __init__(self):
        self.groq_client = GROQ_CLIENT

    async def execute(self, audio: UploadFile, source_lang: str) -> str:
        audio_bytes = await audio.read()
        filename = audio.filename or "audio.wav"

        transcription = self.groq_client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model="whisper-large-v3-turbo",
            language=source_lang,
        )

        return transcription.text
