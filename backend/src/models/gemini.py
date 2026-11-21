from config import GEMINI_CLIENT


class GeminiTranslator:
    def __init__(self):
        self.client = GEMINI_CLIENT

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        prompt = f"""
            Translate the following text from {source_lang} to {target_lang}. 
            Return ONLY the translation.
            Do not add explanations, notes, quotation marks, or alternatives.
            Text: {text}
        """

        response = self.client.models.generate_content(
            model="gemini-2.7-flash", contents=prompt
        )

        return response.text.strip()
