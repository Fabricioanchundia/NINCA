"""Tests for the evaluation harness."""

from ninca.evaluation import Example, evaluate


def _examples() -> list[Example]:
    return [
        Example("a", "attack one", malicious=True),
        Example("b", "attack two", malicious=True),
        Example("c", "benign one", malicious=False),
        Example("d", "benign two", malicious=False),
    ]


def test_perfect_predictor() -> None:
    metrics = evaluate(lambda d: "attack" in d, _examples())
    assert metrics.true_positive == 2
    assert metrics.false_positive == 0
    assert metrics.false_negative == 0
    assert metrics.precision == 1.0
    assert metrics.recall == 1.0
    assert metrics.f1 == 1.0


def test_flags_everything_has_false_positives() -> None:
    metrics = evaluate(lambda _: True, _examples())
    assert metrics.false_positive == 2
    assert metrics.recall == 1.0
    assert metrics.precision == 0.5
