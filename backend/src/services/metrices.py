import evaluate


class TranslationMetrics:
    def __init__(
        self, predictions: list[str], references: list[list[str]], language: str
    ):
        if len(predictions) != len(references):
            raise ValueError(
                f"Number of predictions ({len(predictions)}) ≠ number of references ({len(references)})"
            )

        self.predictions = predictions
        self.references = references
        self.language = language

        # Load metrics once
        self.bleu_metric = evaluate.load("sacrebleu")
        self.chrf_metric = evaluate.load("chrf")
        self.ter_metric = evaluate.load("ter")
        self.bertscore_metric = evaluate.load("bertscore")

    def bleu_score(self):
        result = self.bleu_metric.compute(
            predictions=self.predictions, references=self.references
        )
        return result["score"]

    def chrf_score(self):
        result = self.chrf_metric.compute(
            predictions=self.predictions, references=self.references
        )
        return result["score"]

    def ter_score(self):
        # TER takes one ref per prediction
        ter_references = [refs[0] for refs in self.references]
        result = self.ter_metric.compute(
            predictions=self.predictions, references=ter_references
        )
        return result["score"]

    def bert_score(self):
        # Return list of precision, recall and F1 scores for each record
        result = self.bertscore_metric.compute(
            predictions=self.predictions, references=self.references, lang=self.language
        )
        # Average F1 score across all records
        return sum(result["f1"]) / len(result["f1"])

    def all(self):
        return {
            "BLEU": self.bleu_score(),
            "TER": self.ter_score(),
            "chrF": self.chrf_score(),
            "BERTScore F1": self.bert_score(),
        }
