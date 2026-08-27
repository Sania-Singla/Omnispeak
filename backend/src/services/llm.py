from config import GROQ_CLIENT, NLLB_LANGUAGE_MAP
from utils.load_model import load_model


class TranslationService:
    def __init__(self):
        self.groq_client = GROQ_CLIENT
        self.tokenizer, self.model = load_model("facebook/nllb-200-distilled-600M")

    def using_groq(self, text: str, source_lang: str, target_lang: str) -> str:
        translation_response = self.groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                # system message to instruct the model what to do & how to behave
                {
                    "role": "system",
                    "content": f"Translate the input text directly from source language with code {source_lang} to target language with code '{target_lang}'. Output ONLY the translation.",
                },
                # the user message on which the action need to be performed
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # controls randomness of the output, lower is more deterministic & higher is more random/rephrased
        )
        return translation_response.choices[0].message.content

    def using_nllb(self, text: str, source_lang: str, target_lang: str) -> str:
        self.tokenizer.src_lang = NLLB_LANGUAGE_MAP[source_lang]

        input_tokens = self.tokenizer(text, return_tensors="pt")

        translated_tokens = self.model.generate(
            **input_tokens,
            forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(
                NLLB_LANGUAGE_MAP[target_lang]
            ),
            max_length=512,
        )

        translated_text = self.tokenizer.batch_decode(
            translated_tokens, skip_special_tokens=True
        )[0]

        return translated_text

    def execute(
        self, text: str, source_lang: str, target_lang: str, provider: str = "nllb"
    ) -> str:
        """Executes translation using the specified provider"""

        if provider == "groq":
            return self.using_groq(text, source_lang, target_lang)
        elif provider == "nllb":
            return self.using_nllb(text, source_lang, target_lang)
        else:
            raise ValueError("Unsupported translation provider")
