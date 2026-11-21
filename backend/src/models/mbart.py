# from utils.validate_req import supports
# from utils.load_model import load_model

# MBART_CODES = {
#     "en": "en_XX",
#     "hi": "hi_IN",
#     "pa": "pa_IN",
# }


# class MBARTTranslator:
#     def __init__(self):
#         self.tokenizer, self.model = load_model(
#             model_name="facebook/mbart-large-50-many-to-many-mmt"
#         )

#     def translate(self, text: str, source_lang: str, target_lang: str) -> str:
#         if not supports("mbart", source_lang, target_lang):
#             raise ValueError(
#                 f"Translation from {source_lang} → {target_lang} is not supported by mbart"
#             )

#         self.tokenizer.src_lang = MBART_CODES[source_lang]

#         inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

#         translated_tokens = self.model.generate(
#             **inputs,
#             forced_bos_token_id=(
#                 self.tokenizer.lang_code_to_id[MBART_CODES[target_lang]]
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

MBART_CODES = {
    "en": "en_XX",
    "hi": "hi_IN",
    "pa": "pa_IN",
}

MBART_LOCK = threading.Lock()


class MBARTTranslator:

    def __init__(self):
        self.tokenizer, self.model = load_model(
            "facebook/mbart-large-50-many-to-many-mmt"
        )

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:

        if not supports("mbart", source_lang, target_lang):
            raise ValueError(
                f"Translation from {source_lang} → {target_lang} is not supported by mbart"
            )

        with MBART_LOCK:

            self.tokenizer.src_lang = MBART_CODES[source_lang]

            inputs = self.tokenizer(
                text,
                return_tensors="pt"
            ).to(self.model.device)

            with torch.inference_mode():

                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.lang_code_to_id[
                        MBART_CODES[target_lang]
                    ],
                    max_length=512,
                )

            return self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0].strip()