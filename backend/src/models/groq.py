from config import GROQ_CLIENT


class GroqTranslator:
    def __init__(self):
        self.client = GROQ_CLIENT

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = f"""
            Translate the following text from {source_lang} to {target_lang}. 
            Return ONLY the translation. 
            Do not add explanations, notes, quotation marks, or alternatives.
            Text: {text}
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # controls randomness of the output, lower is more deterministic & higher is more random/rephrased
        )
        return response.choices[0].message.content
