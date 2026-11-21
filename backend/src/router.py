import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from services.stt import TranscriptionService
from services.translate import TranslationService
from services.tts import SpeechService
from utils.validate_req import available_models
from utils.evaluate import evaluate

router = APIRouter()

stt_service = TranscriptionService()
translation_service = TranslationService()
tts_service = SpeechService()


@router.get("/translation-models")
def get_translation_models(source_lang: str, target_lang: str):
    return available_models(source_lang, target_lang)


@router.post("/audio-translate")
async def audioTranslate(
    source_lang: str = Form(),
    target_lang: str = Form(),
    model_name: str = Form(),
    audio: UploadFile = File(...),
):
    print(
        f"Received audio file: {audio.filename}, source language: {source_lang}, target language: {target_lang}, model name: {model_name}"
    )

    try:
        # 1. Speech-to-text (Assuming stt_service.transcribe is async def)
        transcription = await stt_service.transcribe(audio, lang=source_lang)
        print(f"Transcription: {transcription}")

        # 2. Translation (Runs synchronous translate in a background thread)
        translation = await asyncio.to_thread(
            translation_service.translate,
            transcription,
            source_lang,
            target_lang,
            model_name,
        )
        print(f"Translation: {translation}")

        # 3. Evaluation (Runs synchronous evaluate in a background thread)
        scores = await asyncio.to_thread(
            evaluate, [translation], [[transcription]], source_lang
        )
        print(f"Scores: {scores}")

        # 4. Text-to-speech (Runs synchronous gTTS in a background thread)
        output_filename = await asyncio.to_thread(
            tts_service.dictate, translation, target_lang
        )

        # 5. Audio URL
        audio_url = f"http://127.0.0.1:8000/static/{output_filename}"
        print(f"Audio URL: {audio_url}")

        return {
            "transcription": transcription,
            "translation": translation,
            "audio_url": audio_url,
            "scores": scores,
            "model_name": model_name,
        }

    except ValueError as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/audio-translate-many")
async def audio_translate_many(
    source_lang: str = Form(...),
    target_langs: list[str] = Form(default=[]),
    model_name: str = Form(...),
    audio: UploadFile = File(...),
):
    try:
        # 1. Normalize target languages.
        # Supports both repeated fields and comma-separated values.
        normalized_languages = []

        for item in target_langs:
            for lang in item.split(","):
                lang = lang.strip()

                if lang and lang != source_lang and lang not in normalized_languages:
                    normalized_languages.append(lang)

        print("Source language:", source_lang)
        print("Received target languages:", target_langs)
        print("Languages requiring translation:", normalized_languages)

        # 2. Speech-to-text runs only once.
        transcription = await stt_service.transcribe(audio, lang=source_lang)

        print("Transcription:", transcription)

        # 3. Translate each unique target language.
        async def process_language(target_lang):

            print(f"Processing: {source_lang} -> {target_lang}")

            translation = await asyncio.to_thread(
                translation_service.translate,
                transcription,
                source_lang,
                target_lang,
                model_name,
            )

            print(f"Translation ({target_lang}):", translation)

            # Generate speech for this target language.
            audio_filename = await asyncio.to_thread(
                tts_service.dictate, translation, target_lang
            )

            audio_url = f"http://localhost:8000/static/{audio_filename}"

            return {
                "language": target_lang,
                "translation": translation,
                "audio_url": audio_url,
            }

        # 4. Run translations for the unique target languages.
        # If the list is empty, this returns [].
        results = await asyncio.gather(
            *[process_language(lang) for lang in normalized_languages]
        )

        # 5. Return transcription and translation results.
        return {
            "transcription": transcription,
            "source_lang": source_lang,
            "results": results,
        }

    except ValueError as e:
        print("Validation error:", e)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        print("Translation error:", e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/stt")
async def speechToText(lang: str = Form(), audio: UploadFile = File(...)):
    print(f"Received audio file: {audio.filename}, Language: {lang}")

    try:
        transcription = await stt_service.transcribe(audio, lang)
        print(f"Transcription: {transcription}")

        return {
            "transcription": transcription,
        }

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/tts")
async def textToSpeech(lang: str, text: str):
    print(f"text: {text}, Language: {lang}")

    try:
        output_filename = await asyncio.to_thread(tts_service.dictate, text, lang)
        audio_url = f"http://127.0.0.1:8000/static/{output_filename}"
        print(f"Audio URL: {audio_url}")

        return {
            "audio_url": audio_url,
        }

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/text-translate")
async def textTranslate(source_lang: str, target_lang: str, model_name: str, text: str):
    print(
        f"Received text: {text}, source language: {source_lang}, target language: {target_lang}, model name: {model_name}"
    )

    try:
        translation = await asyncio.to_thread(
            translation_service.translate, text, source_lang, target_lang, model_name
        )
        print(f"Translation: {translation}")

        return {
            "translation": translation,
            "model_name": model_name,
        }

    except ValueError as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        print(f"error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
