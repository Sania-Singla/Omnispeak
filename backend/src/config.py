from pathlib import Path
from google import genai
from groq import Groq

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

GROQ_CLIENT = Groq()
GEMINI_CLIENT = genai.Client()
