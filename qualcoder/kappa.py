"""Cohen's kappa and percent agreement, implemented from scratch.

Only NumPy is used (for the confusion matrix); the kappa formula itself
is plain arithmetic so every step is auditable:

    Po = (number of agreements) / N
    Pe = sum over codes c of P(A=c) * P(B=c)   (chance agreement)
    kappa = (Po - Pe) / (1 - Pe)

Interpretation scale (Landis & Koch, 1977):
    < 0.00  poor,  0.00-0.20 slight,  0.21-0.40 fair,
    0.41-0.60 moderate,  0.61-0.80 substantial,  0.81-1.00 almost perfect
"""
from collections import Counter

import numpy as np

__all__ = [
    "cohens_kappa",
    "percent_agreement",
    "observed_agreement",
    "expected_agreement",
    "confusion_matrix",
    "interpret_kappa",
]


def _validate(labels_a, labels_b):
    a = list(labels_a)
    b = list(labels_b)
    if not a or not b:
        raise ValueError("label lists must not be empty")
    if len(a) != len(b):
        raise ValueError(
            f"coder A has {len(a)} labels but coder B has {len(b)}"
        )
    return a, b


def percent_agreement(labels_a, labels_b):
    """Fraction of excerpts where both coders chose the same code."""
    a, b = _validate(labels_a, labels_b)
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


# Alias with the textbook name.
observed_agreement = percent_agreement


def expected_agreement(labels_a, labels_b):
    """Chance agreement Pe = sum_c P(A=c) * P(B=c)."""
    a, b = _validate(labels_a, labels_b)
    n = len(a)
    count_a = Counter(a)
    count_b = Counter(b)
    codes = set(count_a) | set(count_b)
    return sum((count_a[c] / n) * (count_b[c] / n) for c in codes)


def cohens_kappa(labels_a, labels_b):
    """Cohen's kappa for two coders labelling the same excerpts.

    Edge cases:
    * Perfect agreement with a single code in use (Pe == 1, Po == 1)
      -> 1.0 (there is nothing to disagree about).
    * Pe == 1 but Po < 1 (can only happen with degenerate marginals)
      -> 0.0, since agreement is no better than the forced marginals.
    """
    a, b = _validate(labels_a, labels_b)
    po = percent_agreement(a, b)
    pe = expected_agreement(a, b)
    if abs(1.0 - pe) < 1e-12:
        return 1.0 if abs(po - 1.0) < 1e-12 else 0.0
    return (po - pe) / (1.0 - pe)


def confusion_matrix(labels_a, labels_b, codes=None):
    """Return (codes, matrix) where matrix[i, j] counts A=codes[i], B=codes[j].

    Codes are sorted for determinism unless an explicit order is given.
    """
    a, b = _validate(labels_a, labels_b)
    if codes is None:
        codes = sorted(set(a) | set(b))
    index = {c: i for i, c in enumerate(codes)}
    mat = np.zeros((len(codes), len(codes)), dtype=int)
    for x, y in zip(a, b):
        mat[index[x], index[y]] += 1
    return codes, mat


def interpret_kappa(kappa):
    """Landis & Koch (1977) verbal label for a kappa value."""
    if kappa < 0:
        return "poor (below chance)"
    if kappa <= 0.20:
        return "slight"
    if kappa <= 0.40:
        return "fair"
    if kappa <= 0.60:
        return "moderate"
    if kappa <= 0.80:
        return "substantial"
    return "almost perfect"
