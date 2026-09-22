## Commands:

- core libraries
```bash
pip install torch transformers sentencepiece
```

- for evaluation metrices
```bash 
pip install evaluate sacrebleu bert_score
```

- for mbart 
```bash
pip install tiktoken protobuf
```

- execute the script
```bash 
python nllb.py
``` 
will take long for first time loading the model then caches it (make sure to set HF_HOME user env variable to D drive)

---

## Evaluation Metrics

### BLEU (Bilingual Evaluation Understudy)
* **Type:** Word-matching like n-grams(Precision-based)
* **Concept:** Counts overlapping n-grams (1 to 4 words) between predicted and reference text.
* **Scale:** `0` (no overlap) to `1` (perfect match). Higher is better.

### TER (Translation Edit Rate)
* **Type:** Post-editing effort
* **Concept:** Counts insertions, deletions, substitutions, and shifts needed to change the prediction into the reference.
* **Scale:** `0` (no edits needed) to `1` (completely different). Lower is better.

### CHRF (Character F-score)
* **Type:** Character-matching
* **Concept:** Computes Precision, Recall, and F1-score using character-level matches instead of full words.
* **Scale:** `0` to `1`. Higher indicates better character alignment.

### BERTScore
* **Type:** Semantic embedding
* **Concept:** Generates contextual embeddings via BERT and calculates token-level cosine similarity.
* **Scale:** `0` to `1`. Higher indicates better semantic alignment.

---

## 🏆 NLLB is the winner (highest BLEU, chrF, BERT scores & lowest TER score)