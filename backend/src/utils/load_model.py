from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


def load_model(model_name: str):
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    print("Loading model...")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(DEVICE)
    
    print("Model loaded successfully!")
    
    return tokenizer, model
