from datasets import load_dataset
import pandas as pd
from pathlib import Path


# ==========================================
# 1. Load FLORES-200 devtest
# ==========================================

print("Loading FLORES-200...")

ds = load_dataset(
    "facebook/flores",
    "all",
    split="devtest"
)

print(f"Loaded {len(ds)} sentences.")


# ==========================================
# 2. Extract required languages
# ==========================================

df = ds.to_pandas()

english = df["sentence_eng_Latn"]
hindi = df["sentence_hin_Deva"]
punjabi = df["sentence_pan_Guru"]


# ==========================================
# 3. Create all 6 translation directions
# ==========================================

directions = [
    ("en", "hi", english, hindi),
    ("hi", "en", hindi, english),

    ("pa", "hi", punjabi, hindi),
    ("hi", "pa", hindi, punjabi),

    ("pa", "en", punjabi, english),
    ("en", "pa", english, punjabi),
]


rows = []
row_id = 1

for source_lang, target_lang, source_sentences, target_sentences in directions:

    for source_text, target_text in zip(
        source_sentences,
        target_sentences
    ):

        rows.append({
            "id": row_id,
            "source_language": source_lang,
            "target_language": target_lang,
            "input": source_text,
            "expected": target_text,
        })

        row_id += 1


# ==========================================
# 4. Create final DataFrame
# ==========================================

final_df = pd.DataFrame(rows)


# ==========================================
# 5. Save CSV
# ==========================================

output_path = Path(
    "datasets/flores200_benchmark.csv"
)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_csv(
    output_path,
    index=False,
    encoding="utf-8"
)


# ==========================================
# 6. Print summary
# ==========================================

print("\n========================================")
print("FLORES benchmark created successfully!")
print("========================================")

print(f"File: {output_path}")
print(f"Total rows: {len(final_df)}")

print("\nRows per language pair:")

print(
    final_df.groupby(
        ["source_language", "target_language"]
    ).size()
)

print("\nFirst 10 rows:")
print(final_df.head(10).to_string(index=False))