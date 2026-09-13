from google import genai
import os


class GeminiTranslator:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-3.7-flash"

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

        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )

        return response.text.strip()
