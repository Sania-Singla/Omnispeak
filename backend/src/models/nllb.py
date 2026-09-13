from utils.load_model import load_model
from constants import NLLB_LANGUAGE_MAP


class NLLBTranslator:
    MODEL_NAME = "facebook/nllb-200-distilled-600M"

    def __init__(self):
        self.tokenizer, self.model = load_model(self.MODEL_NAME)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        self.tokenizer.src_lang = NLLB_LANGUAGE_MAP[source_lang]

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=(
                self.tokenizer.convert_tokens_to_ids(NLLB_LANGUAGE_MAP[target_lang])
            ),
            max_length=512
        )

        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[
            0
        ].strip()
