from utils.load_model import load_model
from constants import M2M100_LANGUAGE_MAP


class M2M100Translator:
    MODEL_NAME = "facebook/m2m100_418M"

    def __init__(self):
        self.tokenizer, self.model = load_model(self.MODEL_NAME)

    def translate(self, text, source_lang, target_lang):

        self.tokenizer.src_lang = M2M100_LANGUAGE_MAP[source_lang]

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=(
                self.tokenizer.get_lang_id(M2M100_LANGUAGE_MAP[target_lang])
            ),
            max_length=512
        )

        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[
            0
        ].strip()

