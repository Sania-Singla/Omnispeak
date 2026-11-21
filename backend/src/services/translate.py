from models.nllb import NLLBTranslator
from models.m2m100 import M2M100Translator
from models.mbart import MBARTTranslator
from models.marianMT import MarianTranslator
from models.gemini import GeminiTranslator
from models.groq import GroqTranslator


class TranslationService:
    def __init__(self):
        self._translators = {}  # Lazy-loaded translators

    # private members

    def _get_translator(self, model_name: str):
        # Already loaded
        if model_name in self._translators:
            return self._translators[model_name]

        # Load translator
        if model_name == "nllb":
            translator = NLLBTranslator()
        elif model_name == "m2m100":
            translator = M2M100Translator()
        elif model_name == "mbart":
            translator = MBARTTranslator()
        elif model_name == "marian":
            translator = MarianTranslator()
        elif model_name == "gemini":
            translator = GeminiTranslator()
        elif model_name == "groq":
            translator = GroqTranslator()
        else:
            raise ValueError(f"Unsupported translation model: {model_name}")

        # Cache translator
        self._translators[model_name] = translator
        return translator

    def translate(
        self, text: str, source_lang: str, target_lang: str, model_name: str = "nllb"
    ) -> str:
        if not text or str(text).strip() == "":
            return ""

        translator = self._get_translator(model_name)

        return translator.translate(
            text,
            source_lang,
            target_lang,
        )
