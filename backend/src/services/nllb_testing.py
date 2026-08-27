import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/nllb-200-distilled-600M"

print("1 - loading tokenizer")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

print("2 - loading model")
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

model.eval()

print("3 - model loaded")
print("device:", next(model.parameters()).device)

text = "Hello, how are you?"

tokenizer.src_lang = "eng_Latn"

print("4 - tokenizing")
inputs = tokenizer(text, return_tensors="pt")

print("5 - generating")

with torch.no_grad():
    output = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids("pan_Guru"),
        max_length=128,
    )

print("6 - generated")

result = tokenizer.batch_decode(output, skip_special_tokens=True)[0]

print("Result:", result)
