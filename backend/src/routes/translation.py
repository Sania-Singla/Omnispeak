from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.llm import TranslationService
from services.stt import TranscriptionService
from services.tts import SpeechService

router = APIRouter()

stt = TranscriptionService()
llm = TranslationService()
tts = SpeechService()


@router.post("/translate")
async def translate(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
):
    print(
        f"Received audio file: {audio.filename}, source language: {source_lang} and target language: {target_lang}"
    )

    try:
        transcription = await stt.execute(audio, source_lang)
        print(f"Transcription: {transcription}")

        translation = llm.execute(
            transcription, source_lang, target_lang, provider="nllb"
        )
        print(f"Translated text: {translation}")

        output_filename = tts.execute(translation, target_lang)

        audio_url = f"http://127.0.0.1:8000/static/{output_filename}"

        return {
            "transcription": transcription,
            "translation": translation,
            "audio": audio_url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
