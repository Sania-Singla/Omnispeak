import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(model_name: str):
    print(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    print(f"Loading model: {model_name}")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model = model.to(DEVICE)
    model.eval()

    print(f"Model loaded successfully: {model_name}")
    print(f"Device: {DEVICE}")

    return tokenizer, model
