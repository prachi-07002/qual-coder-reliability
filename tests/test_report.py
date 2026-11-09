"""Tests for the per-code report, disagreement listing and loader."""
import unittest
from pathlib import Path

from qualcoder import (
    disagreements,
    load_coding_file,
    load_csv,
    per_code_report,
    summarize,
)

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_coding.csv"


class TestPerCodeReport(unittest.TestCase):
    def test_perfect_code_scores_one(self):
        report = per_code_report(["a", "b"], ["a", "b"])
        self.assertEqual(report["a"]["agreement"], 1.0)
        self.assertEqual(report["a"]["both"], 1)
        self.assertEqual(report["a"]["a_only"], 0)

    def test_partial_code(self):
        # a: [x, x, y], b: [x, y, y] -> x: both=1, a_only=1, b_only=0, union=2
        report = per_code_report(["x", "x", "y"], ["x", "y", "y"])
        self.assertEqual(report["x"]["both"], 1)
        self.assertEqual(report["x"]["a_only"], 1)
        self.assertEqual(report["x"]["union"], 2)
        self.assertAlmostEqual(report["x"]["agreement"], 0.5)
        self.assertAlmostEqual(report["y"]["agreement"], 0.5)

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            per_code_report(["a"], ["a", "b"])


class TestSampleData(unittest.TestCase):
    def setUp(self):
        self.rows = load_csv(SAMPLE)
        self.summary = summarize(self.rows)

    def test_loads_25_fictional_excerpts(self):
        self.assertEqual(len(self.rows), 25)
        self.assertTrue(all(r["excerpt_id"].startswith("E") for r in self.rows))
        self.assertEqual(
            set(r["coder_a"] for r in self.rows)
            | set(r["coder_b"] for r in self.rows),
            {"genai_helpful", "genai_concern", "equity", "engagement", "confusion"},
        )

    def test_five_disagreements_listed(self):
        dis = disagreements(self.rows)
        self.assertEqual(len(dis), 5)
        self.assertEqual(
            [r["excerpt_id"] for r in dis], ["E05", "E10", "E14", "E19", "E24"]
        )

    def test_worst_code_is_confusion_best_is_genai_helpful(self):
        per = self.summary["per_code"]
        worst = min(per, key=lambda c: per[c]["agreement"])
        best = max(per, key=lambda c: per[c]["agreement"])
        self.assertEqual(worst, "confusion")
        self.assertAlmostEqual(per["confusion"]["agreement"], 0.50)
        self.assertEqual(best, "genai_helpful")
        self.assertAlmostEqual(per["genai_helpful"]["agreement"], 5 / 6)

    def test_loader_rejects_missing_column(self):
        import csv
        import tempfile

        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["excerpt_id", "excerpt", "coder_a"])
            writer.writerow(["E01", "hello", "equity"])
            bad = f.name
        with self.assertRaises(ValueError):
            load_coding_file(bad)

    def test_loader_rejects_unsupported_type(self):
        with self.assertRaises(ValueError):
            load_coding_file("data/codebook.md")


if __name__ == "__main__":
    unittest.main()
