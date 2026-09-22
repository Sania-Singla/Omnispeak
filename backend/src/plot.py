import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Read directly from the CSV file
df = pd.read_csv("scores.csv")

# 2. Clean column and language pair strings
df.columns = df.columns.str.strip()
df["pair"] = df["type"].astype(str).str.strip()

# 3. Scale BERTScore to 0-100 to align axes
df["BERTScore F1 (%)"] = pd.to_numeric(df["BERTScore F1"], errors="coerce") * 100

for col in ["BLEU", "TER", "chrF"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

language_pairs = sorted(df["pair"].unique())
metrics = ["BLEU", "chrF", "BERTScore F1 (%)", "TER"]
colors = ["#2b5c8f", "#3caea3", "#f6d55c", "#ed553b"]

# 4. Create 3x2 grid layout for all 6 language pairs
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(16, 14), sharey=False)
axes = axes.flatten()

for idx, pair in enumerate(language_pairs):
    ax = axes[idx]
    sub_df = df[df["pair"] == pair].copy()

    # Sort models by BLEU descending
    sub_df = sub_df.sort_values(by="BLEU", ascending=False)

    models = sub_df["model_name"].tolist()
    x = np.arange(len(models))
    width = 0.2

    for m_idx, metric in enumerate(metrics):
        offset = (m_idx - 1.5) * width
        ax.bar(
            x + offset,
            sub_df[metric],
            width,
            label=f"{metric} (lower better)" if metric == "TER" else metric,
            color=colors[m_idx],
            alpha=0.9,
        )

    ax.set_title(f"Language Pair: {pair}", fontsize=13, fontweight="bold", pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11, fontweight="bold")
    ax.set_ylabel("Score / %", fontsize=10)
    ax.set_ylim(0, 115)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Show legend only on the first subplot
    if idx == 0:
        ax.legend(loc="upper right", frameon=True, fontsize=9)

# Hide extra subplots if fewer than 6 pairs exist
for j in range(len(language_pairs), len(axes)):
    fig.delaxes(axes[j])

plt.suptitle(
    "Translation Model Benchmark Across Language Pairs",
    fontsize=16,
    fontweight="bold",
    y=0.99,
)
plt.tight_layout()
plt.savefig("model_comparison_by_language_pair.png", dpi=300)
plt.show()
