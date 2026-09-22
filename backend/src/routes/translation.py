from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.llm import TranslationService
from services.stt import TranscriptionService
from services.tts import SpeechService
from services.model_registry import ModelRegistry

from evaluation import evaluate

router = APIRouter()

stt = TranscriptionService()
llm = TranslationService()
tts = SpeechService()


@router.post("/translate")
async def translate(
    source_lang: str = Form(),
    target_lang: str = Form(),
    provider: str = Form(),
    audio: UploadFile = File(...),
):
    print(
        f"Received audio file: {audio.filename}, "
        f"source language: {source_lang}, "
        f"target language: {target_lang}, "
        f"provider: {provider}"
    )

    # Validate model + language pair
    if not ModelRegistry.supports(
        provider,
        source_lang,
        target_lang,
    ):
        raise HTTPException(
            status_code=400,
            detail=(f"{provider} does not support " f"{source_lang} -> {target_lang}"),
        )

    try:
        # 1. Speech-to-text
        transcription = await stt.execute(
            audio,
            source_lang,
        )

        print(f"Transcription: {transcription}")

        # 2. Translation
        translation = llm.execute(
            transcription,
            source_lang,
            target_lang,
            provider=provider,
        )

        print(f"Translation: {translation}")

        # 3. evaluation
        scores = evaluate([translation], [[transcription]], source_lang)

        # 4. Text-to-speech
        output_filename = tts.execute(
            translation,
            target_lang,
        )

        # 5. Audio URL
        audio_url = f"http://127.0.0.1:8000/static/{output_filename}"

        return {
            "transcription": transcription,
            "translation": translation,
            "audio": audio_url,
            "scores": scores,
            "provider": provider,
        }

    except Exception as e:
        print(f"error: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/translation-models")
async def get_translation_models(
    source_lang: str,
    target_lang: str,
):
    return ModelRegistry.available_models(
        source_lang,
        target_lang,
    )
