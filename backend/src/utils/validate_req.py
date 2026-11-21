SUPPORTED_PAIRS = {
    "nllb": {
        ("en", "hi"),
        ("hi", "en"),
        ("en", "pa"),
        ("pa", "en"),
        ("hi", "pa"),
        ("pa", "hi"),
    },
    "groq": {
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
    "marianMT": {
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
}


def supports(model_name: str, source_lang: str, target_lang: str) -> bool:
    return (source_lang, target_lang) in SUPPORTED_PAIRS.get(model_name, set())


def available_models(source_lang, target_lang):
    return [
        model_name
        for model_name, pairs in SUPPORTED_PAIRS.items()
        if (source_lang, target_lang) in pairs
    ]
