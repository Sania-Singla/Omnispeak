from metrices import TranslationMetrics
import csv


def evaluate_results(file_path: str):
    predictions = []
    references = []
    source_lang = None

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        source_lang = next(reader)[
            "source_language"
        ]  # Get the source language from the first row

        for row in reader:
            predictions.append(row["predicted"])
            references.append(
                [row["expected"]]
            )  # list of list because some scores (scareBLEU) supports multiple references per prediction

    translation_metrics = TranslationMetrics(predictions, references, source_lang)
    scores = translation_metrics.all()

    return scores


def compare_results(file_paths: list[str]):
    results = {}

    for file_path in file_paths:
        scores = evaluate_results(file_path)
        results[file_path] = scores

    print("Comparison of Evaluation Scores:")

    for file_path, scores in results.items():
        print(f"\n{file_path} Scores:")
        for metric, score in scores.items():
            print(f"{metric}: {score:.4f}")


compare_results(
    [
        "results/nllb/hi_to_en.csv",
        # "results/nllb/hi_to_pa.csv",
        # "results/nllb/pa_to_hi.csv",
        # "results/nllb/pa_to_en.csv",
        # "results/nllb/en_to_pa.csv",
        # "results/nllb/en_to_hi.csv",
        # "results/m2m100/pa_to_hi.csv",
        # "results/m2m100/pa_to_en.csv",
        # "results/m2m100/hi_to_pa.csv",
        "results/m2m100/hi_to_en.csv",
        # "results/m2m100/en_to_hi.csv",
        # "results/m2m100/en_to_pa.csv",
        # "results/mbart/en_to_hi.csv",
        "results/mbart/hi_to_en.csv",
    ]
)
