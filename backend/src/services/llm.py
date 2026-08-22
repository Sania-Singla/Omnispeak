class TranslationService:
    def __init__(self, client):
        self.client = client

    def execute(self, text: str, target_lang: str) -> str:
        translation_response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                # system message to instruct the model what to do & how to behave
                {
                    "role": "system",
                    "content": f"Translate the input text directly into language code '{target_lang}'. Output ONLY the translation.",
                },
                # the user message on which the action need to be performed
                {"role": "user", "content": text},
            ],
            temperature=0.3,  # controls randomness of the output, lower is more deterministic & higher is more random/rephrased
        )
        return translation_response.choices[0].message.content
