from config import GROQ_CLIENT


class GroqTranslator:
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


# from utils.csv import translate_files

# translate_files(
#     [
#         "datasets/hi_to_en.csv",
#         "datasets/en_to_hi.csv",
#         "datasets/pa_to_en.csv",
#         "datasets/pa_to_hi.csv",
#         "datasets/hi_to_pa.csv",
#         "datasets/en_to_pa.csv",
#     ],
#     [
#         "results/groq/hi_to_en.csv",
#         "results/groq/en_to_hi.csv",
#         "results/groq/pa_to_en.csv",
#         "results/groq/pa_to_hi.csv",
#         "results/groq/hi_to_pa.csv",
#         "results/groq/en_to_pa.csv",
#     ],
#     GroqTranslator().translate,
# )
