import uuid
from gtts import gTTS
from config import TEMP_DIR


class SpeechService:
    def __init__(self):
        pass

    def execute(self, text: str, target_lang: str) -> str:
        # gTTS(google text-to-speech) natively generates standard MP3 files
        output_filename = f"tts_{uuid.uuid4()}.mp3"
        output_file_path = TEMP_DIR / output_filename

        tts = gTTS(text=text, lang=target_lang)
        tts.save(output_file_path) # save the audio at designated path

        return output_filename
