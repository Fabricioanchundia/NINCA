"""Benchmark detection approaches against the labeled dataset."""

from pathlib import Path

from ninca.ai import classify_description
from ninca.evaluation import evaluate, load_dataset
from ninca.hybrid import scan_tool_hybrid
from ninca.scanner import Tool, scan_tool

DATASET = Path("evaluation/dataset.json")


def _rules_only(description: str) -> bool:
    return bool(scan_tool(Tool("x", description)))


def _ai_only(description: str) -> bool:
    return classify_description(description).malicious


def _hybrid(description: str) -> bool:
    return bool(scan_tool_hybrid(Tool("x", description), use_ai=True))


def main() -> None:
    examples = load_dataset(DATASET)
    print(f"Dataset: {len(examples)} examples\n")
    header = f"{'approach':12} {'precision':>10} {'recall':>8} {'f1':>6} {'FP':>4} {'FN':>4}"
    print(header)
    print("-" * len(header))
    for name, predict in [
        ("rules-only", _rules_only),
        ("ai-only", _ai_only),
        ("hybrid", _hybrid),
    ]:
        metrics = evaluate(predict, examples)
        print(
            f"{name:12} {metrics.precision:>10.2f} {metrics.recall:>8.2f} "
            f"{metrics.f1:>6.2f} {metrics.false_positive:>4} {metrics.false_negative:>4}"
        )


if __name__ == "__main__":
    main()
