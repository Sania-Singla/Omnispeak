from models.nllb import NLLBTranslator
from models.m2m100 import M2M100Translator
from models.mbart import MBARTTranslator
from models.marianMT import MarianTranslator
from models.gemini_flash import GeminiTranslator
from models.groq import GroqTranslator


class TranslationService:

    def __init__(self):
        # Lazy-loaded translators
        self._translators = {}

    def _get_translator(self, provider: str):
        # Already loaded?
        if provider in self._translators:
            return self._translators[provider]

        # Create translator
        if provider == "nllb":
            translator = NLLBTranslator()

        elif provider == "m2m100":
            translator = M2M100Translator()

        elif provider == "mbart":
            translator = MBARTTranslator()

        elif provider == "marian":
            translator = MarianTranslator()

        elif provider == "gemini":
            translator = GeminiTranslator()
            
        elif provider == "groq":
            translator = GroqTranslator()

        else:
            raise ValueError(f"Unsupported translation provider: {provider}")

        # Cache translator
        self._translators[provider] = translator

        return translator

    def execute(
        self, text: str, source_lang: str, target_lang: str, provider: str = "nllb"
    ) -> str:

        translator = self._get_translator(provider)

        return translator.translate(
            text,
            source_lang,
            target_lang,
        )
