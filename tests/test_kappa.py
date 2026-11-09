"""Tests for Cohen's kappa, percent agreement and edge cases.

Hand-computed cases (verified by hand, see comments):
* Case A: 10 items, confusion [[4, 1], [2, 3]] (rows A=yes/no,
  cols B=yes/no). Po = 7/10 = 0.70. Pe = 0.5*0.6 + 0.5*0.4 = 0.50.
  kappa = (0.70 - 0.50) / (1 - 0.50) = 0.40.
* Case B: 20 items, confusion [[8, 2], [1, 9]]. Po = 17/20 = 0.85.
  A marginals 10/20, 10/20; B marginals 9/20, 11/20.
  Pe = 0.5*0.45 + 0.5*0.55 = 0.50. kappa = (0.85-0.50)/0.50 = 0.70.
"""
import unittest

from qualcoder.kappa import (
    cohens_kappa,
    confusion_matrix,
    expected_agreement,
    interpret_kappa,
    percent_agreement,
)


class TestPercentAgreement(unittest.TestCase):
    def test_perfect(self):
        self.assertEqual(percent_agreement(["a", "b", "c"], ["a", "b", "c"]), 1.0)

    def test_none(self):
        self.assertEqual(percent_agreement(["a", "a"], ["b", "b"]), 0.0)

    def test_partial(self):
        self.assertAlmostEqual(
            percent_agreement(["a", "b", "c", "d"], ["a", "x", "c", "y"]), 0.5
        )


class TestCohensKappa(unittest.TestCase):
    def test_perfect_agreement_is_one(self):
        labels = ["genai_helpful", "equity", "confusion", "engagement"]
        self.assertEqual(cohens_kappa(labels, labels), 1.0)

    def test_chance_level_agreement_is_zero(self):
        # A = [0,0,1,1], B = [0,1,0,1]: Po = 0.5, Pe = 0.5 -> kappa 0.
        a = ["yes", "yes", "no", "no"]
        b = ["yes", "no", "yes", "no"]
        self.assertAlmostEqual(percent_agreement(a, b), 0.5)
        self.assertAlmostEqual(expected_agreement(a, b), 0.5)
        self.assertAlmostEqual(cohens_kappa(a, b), 0.0)

    def test_hand_computed_case_a_kappa_0_40(self):
        # Confusion [[4,1],[2,3]]: build labels from the matrix.
        a = ["yes"] * 5 + ["no"] * 5
        b = ["yes"] * 4 + ["no"] + ["yes"] * 2 + ["no"] * 3
        self.assertAlmostEqual(percent_agreement(a, b), 0.70)
        self.assertAlmostEqual(expected_agreement(a, b), 0.50)
        self.assertAlmostEqual(cohens_kappa(a, b), 0.40)

    def test_hand_computed_case_b_kappa_0_70(self):
        # Confusion [[8,2],[1,9]].
        a = ["yes"] * 10 + ["no"] * 10
        b = ["yes"] * 8 + ["no"] * 2 + ["yes"] + ["no"] * 9
        self.assertAlmostEqual(percent_agreement(a, b), 0.85)
        self.assertAlmostEqual(expected_agreement(a, b), 0.50)
        self.assertAlmostEqual(cohens_kappa(a, b), 0.70)

    def test_single_code_everywhere_is_one(self):
        self.assertEqual(cohens_kappa(["x"] * 5, ["x"] * 5), 1.0)

    def test_below_chance_is_negative(self):
        # Coders systematically disagree: Po=0, Pe=0.5 -> kappa=-1.
        self.assertAlmostEqual(
            cohens_kappa(["a", "a", "b", "b"], ["b", "b", "a", "a"]), -1.0
        )

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            cohens_kappa([], [])

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            cohens_kappa(["a", "b"], ["a"])

    def test_sample_data_kappa_is_0_75(self):
        # The bundled sample was constructed so Po=0.80, Pe=0.20.
        from pathlib import Path

        from qualcoder import load_csv, summarize

        sample = Path(__file__).resolve().parent.parent / "data" / "sample_coding.csv"
        rows = load_csv(sample)
        s = summarize(rows)
        self.assertEqual(s["n"], 25)
        self.assertAlmostEqual(s["percent_agreement"], 0.80)
        self.assertAlmostEqual(s["expected_agreement"], 0.20)
        self.assertAlmostEqual(s["kappa"], 0.75)


class TestConfusionMatrix(unittest.TestCase):
    def test_matrix_counts(self):
        codes, mat = confusion_matrix(["a", "a", "b"], ["a", "b", "b"])
        self.assertEqual(codes, ["a", "b"])
        self.assertEqual(mat.tolist(), [[1, 1], [0, 1]])


class TestInterpretation(unittest.TestCase):
    def test_scale(self):
        self.assertEqual(interpret_kappa(0.75), "substantial")
        self.assertEqual(interpret_kappa(1.0), "almost perfect")
        self.assertEqual(interpret_kappa(0.0), "slight")
        self.assertEqual(interpret_kappa(-0.1), "poor (below chance)")


if __name__ == "__main__":
    unittest.main()
