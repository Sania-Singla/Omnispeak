from utils.load_model import load_model


class MarianTranslator:
    MODELS = {
        ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
        ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
        ("pa", "en"): "Helsinki-NLP/opus-mt-pa-en",
    }

    def __init__(self):
        # lazy loading
        self._models = {}

    def _get_model(self, source_lang: str, target_lang: str):

        pair = (source_lang, target_lang)

        if pair not in self.MODELS:
            raise ValueError(
                f"MarianMT does not support " f"{source_lang} -> {target_lang}"
            )

        # If already loaded, reuse it
        if pair in self._models:
            return self._models[pair]

        model_name = self.MODELS[pair]

        print(f"Loading MarianMT model: {model_name}")

        tokenizer, model = load_model(model_name)

        self._models[pair] = (tokenizer, model)

        return tokenizer, model

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        tokenizer, model = self._get_model(source_lang, target_lang)

        inputs = tokenizer(text, return_tensors="pt", truncation=True).to(model.device)

        generated_tokens = model.generate(**inputs, max_length=512)

        translated_text = tokenizer.decode(
            generated_tokens[0], skip_special_tokens=True
        )

        return translated_text.strip()


# from utils.csv import translate_files

# translate_files(
#     [
#         "datasets/hi_to_en.csv",
#         "datasets/en_to_hi.csv",
#         "datasets/pa_to_en.csv",
#     ],
#     [
#         "results/marianMT/hi_to_en.csv",
#         "results/marianMT/en_to_hi.csv",
#         "results/marianMT/pa_to_en.csv",
#     ],
#     MarianTranslator().translate,
# )

# translate_file("datasets/hi_to_en.csv", "results/m2m100/hi_to_en.csv", translate)
