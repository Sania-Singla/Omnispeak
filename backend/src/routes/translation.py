from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.llm import TranslationService
from services.stt import TranscriptionService
from services.tts import SpeechService
from config import GROQ_CLIENT

router = APIRouter()

# Centralized instances of the appropriate client for each service
stt = TranscriptionService(GROQ_CLIENT)
llm = TranslationService(GROQ_CLIENT)
tts = SpeechService()


@router.post("/translate")
async def translate(
    audio: UploadFile = File(...),
    sourceLanguage: str = Form(...),
    targetLanguage: str = Form(...),
):
    print(f"Received audio file: {audio.filename}, target language: {targetLanguage}")

    try:
        audio_bytes = await audio.read()

        transcribed_text = stt.execute(audio_bytes, audio.filename, sourceLanguage)
        print(f"Transcribed text: {transcribed_text}")

        translated_text = llm.execute(transcribed_text, targetLanguage)
        print(f"Translated text: {translated_text}")

        output_filename = tts.execute(translated_text, targetLanguage)

        audio_url = f"http://127.0.0.1:8000/static/{output_filename}"

        return {
            "TranscribedText": transcribed_text,
            "translatedText": translated_text,
            "TranslatedAudioUrl": audio_url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
