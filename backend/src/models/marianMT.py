# from utils.load_model import load_model
# from utils.validate_req import supports

# MODELS = {
#     ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
#     ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
#     ("pa", "en"): "Helsinki-NLP/opus-mt-pa-en",
# }


# class MarianTranslator:
#     def __init__(self):
#         self._models = {}  # lazy loading

#     def _get_model(self, source_lang: str, target_lang: str):
#         pair = (source_lang, target_lang)

#         # Already loaded
#         if pair in self._models:
#             return self._models[pair]

#         tokenizer, model = load_model(MODELS[pair])

#         self._models[pair] = (tokenizer, model)

#         return tokenizer, model

#     def translate(self, text: str, source_lang: str, target_lang: str) -> str:
#         if not supports("marianMT", source_lang, target_lang):
#             raise ValueError(
#                 f"Translation from {source_lang} → {target_lang} is not supported by marianMT"
#             )

#         tokenizer, model = self._get_model(source_lang, target_lang)

#         inputs = tokenizer(text, return_tensors="pt", truncation=True).to(model.device)

#         generated_tokens = model.generate(**inputs, max_length=512)

#         return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[
#             0
#         ].strip()


# # from utils.csv import translate_files

# # translate_files(
# #     [
# #         "datasets/hi_to_en.csv",
# #         "datasets/en_to_hi.csv",
# #         "datasets/pa_to_en.csv",
# #     ],
# #     [
# #         "results/marianMT/hi_to_en.csv",
# #         "results/marianMT/en_to_hi.csv",
# #         "results/marianMT/pa_to_en.csv",
# #     ],
# #     MarianTranslator().translate,
# # )

# # translate_file("datasets/hi_to_en.csv", "results/m2m100/hi_to_en.csv", translate)

import threading
import torch

from utils.load_model import load_model
from utils.validate_req import supports

MODELS = {
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("pa", "en"): "Helsinki-NLP/opus-mt-pa-en",
}

MARIAN_LOCK = threading.Lock()


class MarianTranslator:

    def __init__(self):
        self.models = {}

    def _get_model(self, source_lang: str, target_lang: str):

        pair = (source_lang, target_lang)

        if pair in self.models:
            return self.models[pair]

        with MARIAN_LOCK:

            if pair not in self.models:

                if pair not in MODELS:
                    raise ValueError(f"Unsupported language pair: {pair}")

                tokenizer, model = load_model(MODELS[pair])

                self.models[pair] = (tokenizer, model)

        return self.models[pair]

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:

        if not supports("marianMT", source_lang, target_lang):
            raise ValueError(
                f"Translation from {source_lang} → {target_lang} is not supported by marianMT"
            )

        tokenizer, model = self._get_model(source_lang, target_lang)

        with torch.inference_mode():

            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True
            ).to(model.device)

            generated_tokens = model.generate(
                **inputs,
                max_length=512
            )

        return tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0].strip()