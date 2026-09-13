from groq import Groq
import os
from config import GROQ_CLIENT


class GeminiTranslator:
    def __init__(self):
        self.client = GROQ_CLIENT
        self.model = "openai/gpt-oss-20b"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = f"""
            Translate the following text from
            {source_lang} to {target_lang}.

            Return ONLY the translation.
            Do not add explanations, notes, quotation marks,
            or alternatives.

            Text:
            {text}
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                # system message to instruct the model what to do & how to behave
                {"role": "system", "content": prompt},
                # the user message on which the action need to be performed
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # controls randomness of the output, lower is more deterministic & higher is more random/rephrased
        )
        return response.choices[0].message.content
