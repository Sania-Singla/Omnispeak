from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()  # load env first then import files that might be using env variables

from config import TEMP_DIR
from routes.translation import router as translation_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(TEMP_DIR)), name="static")

app.include_router(translation_router, prefix="")


@app.get("/")
def root():
    return {"message": "Welcome to the Omnispeak API!"}
