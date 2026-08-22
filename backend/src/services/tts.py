import uuid
from config import TEMP_DIR


class SpeechService:
    def __init__(self, client):
        self.client = client

    #! --------------------------------------------------------------------------------------------------
    #! currently translates to english
    #! --------------------------------------------------------------------------------------------------

    def execute(self, text: str) -> str:
        response = self.client.audio.speech.create(
            model="canopylabs/orpheus-v1-english",
            voice="troy",
            input=text,
            response_format="wav",
        )

        output_filename = f"tts_{uuid.uuid4()}.wav"
        output_file_path = TEMP_DIR / output_filename

        # cause we are serving it as a static file so we have to have it stored at our backend server
        response.write_to_file(output_file_path)

        return output_filename
