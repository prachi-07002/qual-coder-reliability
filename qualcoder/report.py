"""Per-code agreement / disagreement report for two coders.

For each code c:
  * both_c      -- excerpts both coders labelled c
  * a_only / b_only -- excerpts only one coder labelled c
  * union       -- excerpts at least one coder labelled c
  * agreement   -- both_c / union  (Jaccard-style per-code agreement;
                   1.0 means the coders never disagreed about c)
"""
from collections import Counter

from .kappa import (
    cohens_kappa,
    confusion_matrix,
    expected_agreement,
    interpret_kappa,
    percent_agreement,
)

__all__ = ["per_code_report", "disagreements", "summarize", "format_report"]


def per_code_report(labels_a, labels_b):
    if len(labels_a) != len(labels_b):
        raise ValueError("label lists must have the same length")
    codes = sorted(set(labels_a) | set(labels_b))
    report = {}
    for code in codes:
        both = sum(1 for a, b in zip(labels_a, labels_b) if a == b == code)
        a_only = sum(1 for a, b in zip(labels_a, labels_b) if a == code and b != code)
        b_only = sum(1 for a, b in zip(labels_a, labels_b) if b == code and a != code)
        union = both + a_only + b_only
        report[code] = {
            "both": both,
            "a_only": a_only,
            "b_only": b_only,
            "union": union,
            "agreement": (both / union) if union else 1.0,
        }
    return report


def disagreements(rows):
    """Rows where the coders differ, as a list of dicts."""
    return [r for r in rows if r["coder_a"] != r["coder_b"]]


def summarize(rows):
    a, b = [r["coder_a"] for r in rows], [r["coder_b"] for r in rows]
    kappa = cohens_kappa(a, b)
    codes, mat = confusion_matrix(a, b)
    return {
        "n": len(rows),
        "codes": codes,
        "confusion_matrix": mat,
        "percent_agreement": percent_agreement(a, b),
        "observed_agreement": percent_agreement(a, b),
        "expected_agreement": expected_agreement(a, b),
        "kappa": kappa,
        "interpretation": interpret_kappa(kappa),
        "per_code": per_code_report(a, b),
        "disagreements": disagreements(rows),
        "coder_a_counts": dict(Counter(a)),
        "coder_b_counts": dict(Counter(b)),
    }


def format_report(summary):
    lines = []
    lines.append("Inter-coder reliability report")
    lines.append("=" * 40)
    lines.append(f"Excerpts coded:        {summary['n']}")
    lines.append(f"Codes:                 {', '.join(summary['codes'])}")
    lines.append(
        f"Percent agreement:     {summary['percent_agreement']:.1%} "
        f"({int(round(summary['percent_agreement'] * summary['n']))}/{summary['n']})"
    )
    lines.append(f"Expected (chance) agr: {summary['expected_agreement']:.3f}")
    lines.append(
        f"Cohen's kappa:         {summary['kappa']:.3f} "
        f"({summary['interpretation']})"
    )
    lines.append("")
    lines.append("Per-code agreement (both / at-least-one-coded):")
    for code, stats in sorted(
        summary["per_code"].items(), key=lambda kv: kv[1]["agreement"]
    ):
        lines.append(
            f"  {code:<16} {stats['agreement']:.2f}  "
            f"(both={stats['both']}, A-only={stats['a_only']}, "
            f"B-only={stats['b_only']})"
        )
    lines.append("")
    lines.append("Confusion matrix (rows = coder A, cols = coder B):")
    codes = summary["codes"]
    lines.append("  " + " ".join(f"{c[:12]:>12}" for c in [""] + codes))
    for code, row in zip(codes, summary["confusion_matrix"]):
        lines.append(f"  {code[:12]:>12}" + "".join(f"{int(v):>12}" for v in row))
    lines.append("")
    dis = summary["disagreements"]
    lines.append(f"Disagreements ({len(dis)}):")
    if not dis:
        lines.append("  none -- perfect agreement")
    for r in dis:
        lines.append(
            f"  [{r['excerpt_id']}] A={r['coder_a']}  B={r['coder_b']}  "
            f"-- {r['excerpt']}"
        )
    return "\n".join(lines)
