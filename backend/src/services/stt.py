class TranscriptionService:
    def __init__(self, client):
        self.client = client

    def execute(self, file_bytes: bytes, filename: str, source_lang: str) -> str:
        transcription = self.client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model="whisper-large-v3-turbo",
            language=source_lang,
        )
        return transcription.text
