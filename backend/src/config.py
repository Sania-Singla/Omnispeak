from pathlib import Path
import os
from groq import Groq

# global variables

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

GROQ_CLIENT = Groq(api_key=os.getenv("GROQ_API_KEY"))
