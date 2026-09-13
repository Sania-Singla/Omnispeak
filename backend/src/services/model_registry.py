class ModelRegistry:
    SUPPORTED_PAIRS = {
        "nllb": {
            ("en", "hi"),
            ("hi", "en"),
            ("en", "pa"),
            ("pa", "en"),
            ("hi", "pa"),
            ("pa", "hi"),
        },
        "m2m100": {
            ("en", "hi"),
            ("hi", "en"),
            ("en", "pa"),
            ("pa", "en"),
            ("hi", "pa"),
            ("pa", "hi"),
        },
        "mbart": {
            ("en", "hi"),
            ("hi", "en"),
        },
        "marian": {
            ("en", "hi"),
            ("hi", "en"),
            ("pa", "en"),
        },
        "gemini": {
            ("en", "hi"),
            ("hi", "en"),
            ("en", "pa"),
            ("pa", "en"),
            ("hi", "pa"),
            ("pa", "hi"),
        },
        "indictrans2": {
            ("en", "hi"),
            ("hi", "en"),
            ("en", "pa"),
            ("pa", "en"),
            ("hi", "pa"),
            ("pa", "hi"),
        },
    }

    @classmethod
    def supports(cls, provider: str, source_lang: str, target_lang: str) -> bool:
        return (source_lang, target_lang) in cls.SUPPORTED_PAIRS.get(provider, set())

    @classmethod
    def available_models(cls, source_lang, target_lang):
        return [
            provider
            for provider, pairs in cls.SUPPORTED_PAIRS.items()
            if (source_lang, target_lang) in pairs
        ]
