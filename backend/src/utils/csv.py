import csv


def write_to_csv(output_path: str, data: list, fieldnames: list):
    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)


def translate_file(file_path: str, output_path: str, translate_func):
    results = []

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            print(f"Translating row {row['id']}...")

            translation = translate_func(
                row["input"], row["source_language"], row["target_language"]
            )

            results.append({**row, "predicted": translation})

    write_to_csv(
        output_path,
        results,
        fieldnames=[
            "id",
            "source_language",
            "target_language",
            "input",
            "expected",
            "predicted",
        ],
    )

    print(f"Results saved to: {output_path}")


def translate_files(file_paths: list[str], output_paths: list[str], translate_func):
    for file_path, output_path in zip(file_paths, output_paths):
        translate_file(file_path, output_path, translate_func)
