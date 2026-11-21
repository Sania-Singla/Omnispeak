# from utils.validate_req import supports
# from utils.load_model import load_model

# NLLB_CODES = {
#     "en": "eng_Latn",
#     "hi": "hin_Deva",
#     "pa": "pan_Guru",
# }


# class NLLBTranslator:
#     def __init__(self):
#         self.tokenizer, self.model = load_model(
#             model_name="facebook/nllb-200-distilled-600M"
#         )

#     def translate(self, text: str, source_lang: str, target_lang: str) -> str:
#         if not supports("nllb", source_lang, target_lang):
#             raise ValueError(
#                 f"Translation from {source_lang} → {target_lang} is not supported by nllb"
#             )

#         self.tokenizer.src_lang = NLLB_CODES[source_lang]

#         inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

#         translated_tokens = self.model.generate(
#             **inputs,
#             forced_bos_token_id=(
#                 self.tokenizer.convert_tokens_to_ids(NLLB_CODES[target_lang])
#             ),
#             max_length=512,
#         )

#         return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[
#             0
#         ].strip()


import threading
import torch

from utils.validate_req import supports
from utils.load_model import load_model

NLLB_CODES = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "pa": "pan_Guru",
}


# Shared lock because the tokenizer's src_lang
# changes depending on the translation request.
NLLB_INFERENCE_LOCK = threading.Lock()


class NLLBTranslator:
    def __init__(self):
        self.tokenizer, self.model = load_model(
            model_name="facebook/nllb-200-distilled-600M"
        )

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not supports("nllb", source_lang, target_lang):
            raise ValueError(
                f"Translation from {source_lang} → "
                f"{target_lang} is not supported by nllb"
            )


        # Protect tokenizer and model inference.
        with NLLB_INFERENCE_LOCK:

            # Set source language.
            self.tokenizer.src_lang = NLLB_CODES[source_lang]

            # Tokenize input.
            inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

            # Generate translated tokens.
            with torch.inference_mode():

                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=(
                        self.tokenizer.convert_tokens_to_ids(NLLB_CODES[target_lang])
                    ),
                    max_length=512,
                )

            # Decode output.
            translation = self.tokenizer.batch_decode(
                translated_tokens, skip_special_tokens=True
            )[0].strip()

            return translation
