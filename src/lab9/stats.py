
"""Statistics for Lab 9: judge calibration and paired evaluation."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.stats import bootstrap

POS = "FAIL"


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    if len(human) != len(judge):
        raise ValueError("Human and judge labels must have the same length.")

    result = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for h, j in zip(human, judge):
        if h not in ("PASS", "FAIL") or j not in ("PASS", "FAIL"):
            raise ValueError("Labels must be PASS or FAIL.")

        if h == POS and j == POS:
            result["tp"] += 1
        elif h != POS and j == POS:
            result["fp"] += 1
        elif h == POS and j != POS:
            result["fn"] += 1
        else:
            result["tn"] += 1

    return result


def precision_recall(
    human: Sequence[str], judge: Sequence[str]
) -> tuple[float, float]:
    cm = confusion(human, judge)

    tp, fp, fn = cm["tp"], cm["fp"], cm["fn"]

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0

    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    cm = confusion(human, judge)

    tp, fp = cm["tp"], cm["fp"]
    fn, tn = cm["fn"], cm["tn"]
    n = tp + fp + fn + tn

    if n == 0:
        raise ValueError("Cannot compute kappa for empty data.")

    observed = (tp + tn) / n

    human_fail = (tp + fn) / n
    human_pass = (fp + tn) / n
    judge_fail = (tp + fp) / n
    judge_pass = (fn + tn) / n

    expected = human_fail * judge_fail + human_pass * judge_pass

    if abs(1 - expected) < 1e-12:
        raise ValueError("Kappa is undefined.")

    return (observed - expected) / (1 - expected)


def rogan_gladen(
    observed_rate: float, sensitivity: float, specificity: float
) -> float:
    denominator = sensitivity + specificity - 1

    if abs(denominator) < 1e-12:
        raise ValueError("Rogan-Gladen denominator is zero.")

    corrected = (observed_rate + specificity - 1) / denominator

    return max(0.0, min(1.0, corrected))


def paired_bootstrap(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_resamples: int = 1000,
    rng: int = 2027,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """Bootstrap paired differences on the same evaluation items."""
    if len(a) != len(b) or not a:
        raise ValueError("Paired samples must be nonempty and equally sized.")

    a_array = np.asarray(a, dtype=float)
    b_array = np.asarray(b, dtype=float)

    differences = a_array - b_array
    delta = float(np.mean(differences))

    if np.all(differences == 0):
        return (0.0, 0.0, 0.0)

    result = bootstrap(
        (a_array, b_array),
        statistic=lambda x, y: np.mean(x - y),
        paired=True,
        n_resamples=n_resamples,
        method="percentile",
        rng=np.random.default_rng(rng),
        confidence_level=confidence,
    )

    return (
        delta,
        float(result.confidence_interval.low),
        float(result.confidence_interval.high),
    )


def pass_at_k(n: int, c: int, k: int) -> float:
    """M6: Advanced — implement in the later checkpoint."""
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """M6: Advanced — implement in the later checkpoint."""
    raise NotImplementedError
