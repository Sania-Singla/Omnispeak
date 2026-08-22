from pathlib import Path
from groq import Groq
import os

# global variables
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)
GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))
