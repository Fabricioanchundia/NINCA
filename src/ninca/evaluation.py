"""Evaluate detection approaches against a labeled dataset."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Example:
    """A labeled tool description."""

    name: str
    description: str
    malicious: bool


@dataclass(frozen=True, slots=True)
class Metrics:
    """Confusion matrix and derived scores for one approach."""

    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def precision(self) -> float:
        predicted = self.true_positive + self.false_positive
        return self.true_positive / predicted if predicted else 0.0

    @property
    def recall(self) -> float:
        actual = self.true_positive + self.false_negative
        return self.true_positive / actual if actual else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def load_dataset(path: Path) -> list[Example]:
    """Load labeled examples from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    raw = data.get("examples", data) if isinstance(data, dict) else data
    examples: list[Example] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                examples.append(
                    Example(
                        name=str(item.get("name", "")),
                        description=str(item.get("description", "")),
                        malicious=bool(item.get("malicious", False)),
                    )
                )
    return examples


def evaluate(predict: Callable[[str], bool], examples: Iterable[Example]) -> Metrics:
    """Run a predictor over the dataset and compute a confusion matrix."""
    tp = fp = tn = fn = 0
    for example in examples:
        predicted = predict(example.description)
        if example.malicious and predicted:
            tp += 1
        elif example.malicious and not predicted:
            fn += 1
        elif not example.malicious and predicted:
            fp += 1
        else:
            tn += 1
    return Metrics(tp, fp, tn, fn)
