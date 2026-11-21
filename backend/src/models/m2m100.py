# from utils.validate_req import supports
# from utils.load_model import load_model

# M2M100_CODES = {
#     "en": "en",
#     "hi": "hi",
#     "pa": "pa",
# }


# class M2M100Translator:
#     def __init__(self):
#         self.tokenizer, self.model = load_model(model_name="facebook/m2m100_418M")

#     def translate(self, text, source_lang, target_lang):
#         if not supports("m2m100", source_lang, target_lang):
#             raise ValueError(
#                 f"Translation from {source_lang} → {target_lang} is not supported by m2m100"
#             )

#         self.tokenizer.src_lang = M2M100_CODES[source_lang]

#         inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

#         translated_tokens = self.model.generate(
#             **inputs,
#             forced_bos_token_id=(self.tokenizer.get_lang_id(M2M100_CODES[target_lang])),
#             max_length=512,
#         )

#         return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[
#             0
#         ].strip()


import threading
import torch

from utils.validate_req import supports
from utils.load_model import load_model

M2M100_CODES = {
    "en": "en",
    "hi": "hi",
    "pa": "pa",
}

M2M100_LOCK = threading.Lock()


class M2M100Translator:

    def __init__(self):
        self.tokenizer, self.model = load_model(
            "facebook/m2m100_418M"
        )

    def translate(self, text, source_lang, target_lang):

        if not supports("m2m100", source_lang, target_lang):
            raise ValueError(
                f"Translation from {source_lang} → {target_lang} is not supported by m2m100"
            )

        with M2M100_LOCK:

            self.tokenizer.src_lang = M2M100_CODES[source_lang]

            inputs = self.tokenizer(
                text,
                return_tensors="pt"
            ).to(self.model.device)

            with torch.inference_mode():

                translated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.get_lang_id(
                        M2M100_CODES[target_lang]
                    ),
                    max_length=512,
                )

            return self.tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0].strip()