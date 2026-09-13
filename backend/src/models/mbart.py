from utils.load_model import load_model
from constants import MBART_LANGUAGE_MAP


class MBARTTranslator:
    MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"

    def __init__(self):
        self.tokenizer, self.model = load_model(self.MODEL_NAME)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        self.tokenizer.src_lang = MBART_LANGUAGE_MAP[source_lang]

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=(
                self.tokenizer.lang_code_to_id[MBART_LANGUAGE_MAP[target_lang]]
            ),
            max_length=512,
        )

        return self.tokenizer.decode(
            translated_tokens[0], skip_special_tokens=True
        ).strip()
