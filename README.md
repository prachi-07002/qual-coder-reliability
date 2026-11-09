# qual-coder-reliability

A small, dependency-light tool for **inter-coder reliability** in
qualitative research: two coders label the same excerpts, and the tool
reports how much they agree — beyond what chance alone would explain.

Built for Prachi Payasi's Spring 2027 Honors College research project
**"Analyzing STEM Education Interventions via Qualitative Data
Analysis"** (Prof. Lisa B. Bosman), which codes student responses about
interventions including GenAI in Project Management, Social Justice in
Calculus, and Autoethnography with the PMaster Game. In that project,
showing that two coders independently reach the same codes is how you
demonstrate that the findings are trustworthy, not just one person's
reading — Cohen's kappa is the standard statistic for exactly that.

## Headline results (bundled sample data)

25 fictional excerpts, 5 codes, 2 coders:

| Metric | Value |
|---|---|
| Percent agreement | **80.0% (20/25)** |
| Expected (chance) agreement | 0.200 |
| **Cohen's kappa** | **0.750 — "substantial"** (Landis & Koch) |
| Disagreements | 5, listed with excerpt IDs |

Per-code agreement (both coders / at-least-one-coded):

| Code | Agreement | Notes |
|---|---|---|
| `genai_helpful` | **0.83 — best** | both=5, A-only=1, B-only=0 |
| `equity` | 0.80 | both=4, A-only=1, B-only=0 |
| `genai_concern` | 0.67 | both=4, A-only=1, B-only=1 |
| `engagement` | 0.57 | both=4, A-only=1, B-only=2 |
| `confusion` | **0.50 — worst** | both=3, A-only=1, B-only=2 |

The worst codes point at real work, not just a number: `confusion`
vs `engagement` disagree on excerpts like E19/E24, where a student is
both lost *and* enjoying the game — the codebook needs a rule for
which theme dominates before a second coding round (see
`data/codebook.md`).

## How to run

Requires Python 3.10+ and NumPy only (stdlib otherwise).

```bash
# Demo: analyse the bundled sample data
python3 main.py

# Analyse your own coding file (CSV or JSON)
python3 main.py path/to/coding.csv
python3 main.py path/to/coding.csv --json   # machine-readable summary
```

Input format (`excerpt_id, excerpt, coder_a, coder_b`):

```csv
excerpt_id,excerpt,coder_a,coder_b
E01,"The chatbot drafted our timeline...",genai_helpful,genai_helpful
```

## How to run the tests

```bash
python3 -m unittest discover -s tests -v
# 22 tests, all passing
```

Tests include known kappa values verified by hand: perfect agreement
→ κ = 1.0, chance-level agreement → κ ≈ 0, a hand-computed
10-item case → κ = 0.40 (Po = 0.70, Pe = 0.50), a hand-computed
20-item case → κ = 0.70 (Po = 0.85, Pe = 0.50), and the sample data
itself → κ = 0.75 (Po = 0.80, Pe = 0.20). Edge cases (empty input,
mismatched lengths, single-code data, below-chance agreement) are
covered too.

## What it does

- **`qualcoder/kappa.py`** — Cohen's kappa from scratch: observed vs
  expected agreement, confusion matrix (NumPy), Landis & Koch
  interpretation; handles the Pe = 1 edge case.
- **`qualcoder/loader.py`** — loads a coded CSV or JSON file and
  validates columns / blank labels.
- **`qualcoder/report.py`** — per-code agreement/disagreement report
  (both / A-only / B-only counts) and a printable report that lists
  every disagreement with its excerpt.
- **`main.py`** — CLI: loads the sample by default, or any CSV/JSON
  path; `--json` for a machine-readable summary.
- **`data/sample_coding.csv`** — 25 fictional excerpts across the
  codebook `genai_helpful`, `genai_concern`, `equity`, `engagement`,
  `confusion` (no real personal data). `data/codebook.md` documents
  each code and the coding rules.

## Interpreting kappa (Landis & Koch, 1977)

| Kappa | Strength |
|---|---|
| < 0.00 | Poor (below chance) |
| 0.00–0.20 | Slight |
| 0.21–0.40 | Fair |
| 0.41–0.60 | Moderate |
| 0.61–0.80 | Substantial |
| 0.81–1.00 | Almost perfect |

Kappa matters because raw percent agreement flatters you: if one code
dominates, two coders can agree most of the time by chance alone.
Kappa subtracts that chance agreement, so 0.75 means the coders agree
substantially *more* than chance — the standard bar for reporting a
qualitative coding scheme as reliable (typically κ ≥ 0.61, and ≥ 0.80
for high-stakes claims).

## Application talking point

> "I built a Python tool that measures inter-coder reliability for qualitative coding — on sample data from the GenAI / social-justice / PMaster interventions it reached Cohen's kappa 0.75 (substantial agreement, 80% raw agreement) and pinpointed `confusion` vs `engagement` as the code pair needing a clearer codebook rule before a second coding round."
