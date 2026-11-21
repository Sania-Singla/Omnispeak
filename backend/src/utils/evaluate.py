import csv
from services.metrices import TranslationMetrics


# evaluate single output
def evaluate(predictions: list[str], references: list[list[str]], source_lang: str):
    translation_metrics = TranslationMetrics(predictions, references, source_lang)
    scores = translation_metrics.all()
    return scores


# evaluate a file
def evaluate_results(file_path: str):
    predictions = []
    references = []
    source_lang = None

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Process all rows without skipping the first record
        for row in reader:
            if source_lang is None:
                source_lang = row.get("source_language")

            # Supports both 'output' and 'predicted' column headers
            pred_text = row.get("output") or row.get("predicted", "")
            predictions.append(pred_text)
            references.append([row.get("expected", "")])

    translation_metrics = TranslationMetrics(predictions, references, source_lang)
    scores = translation_metrics.all()

    return scores


# evaluate multiple files and save results to "scores.csv"
def compare_results(file_paths: list[str], output_csv: str = "scores.csv"):
    results = {}

    print("Comparison of Evaluation Scores:")
    for file_path in file_paths:
        scores = evaluate_results(file_path)
        results[file_path] = scores

        print(f"\n{file_path} Scores:")
        for metric, score in scores.items():
            print(f"{metric}: {score:.4f}")

    # Write evaluation scores to scores.csv
    if results:
        # Collect all metric keys across files to form header columns
        metric_keys = list(next(iter(results.values())).keys())
        fieldnames = ["file_path"] + metric_keys

        with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for file_path, scores in results.items():
                row = {"file_path": file_path}
                row.update(scores)
                writer.writerow(row)

        print(f"\nSaved results to {output_csv}")


# compare_results(
#     [
#         "results/nllb/hi_to_en.csv",
#         "results/nllb/hi_to_pa.csv",
#         "results/nllb/pa_to_hi.csv",
#         "results/nllb/pa_to_en.csv",
#         "results/nllb/en_to_pa.csv",
#         "results/nllb/en_to_hi.csv",

#         "results/gemini/hi_to_en.csv",
#         "results/gemini/hi_to_pa.csv",
#         "results/gemini/pa_to_hi.csv",
#         "results/gemini/pa_to_en.csv",
#         "results/gemini/en_to_pa.csv",
#         "results/gemini/en_to_hi.csv",

#         "results/groq/hi_to_en.csv",
#         "results/groq/hi_to_pa.csv",
#         "results/groq/pa_to_hi.csv",
#         "results/groq/pa_to_en.csv",
#         "results/groq/en_to_pa.csv",
#         "results/groq/en_to_hi.csv",

#         "results/m2m100/hi_to_en.csv",
#         "results/m2m100/hi_to_pa.csv",
#         "results/m2m100/pa_to_hi.csv",
#         "results/m2m100/pa_to_en.csv",
#         "results/m2m100/en_to_pa.csv",
#         "results/m2m100/en_to_hi.csv",

#         "results/marianmt/pa_to_en.csv",
#         "results/marianmt/hi_to_en.csv",
#         "results/marianmt/en_to_hi.csv",

#         "results/mbart/en_to_hi.csv",
#         "results/mbart/hi_to_en.csv",
#     ],
#     output_csv="scores.csv",
# )
