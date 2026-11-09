#!/usr/bin/env python3
"""CLI for qual-coder-reliability.

Usage:
    python main.py                    # demo: analyse the bundled sample data
    python main.py data/sample_coding.csv
    python main.py path/to/coding.csv --json   # machine-readable summary
"""
import argparse
import json
import sys
from pathlib import Path

from qualcoder import format_report, load_coding_file, summarize


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inter-coder reliability for qualitative coding "
        "(Cohen's kappa, percent agreement, per-code report)."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=Path(__file__).parent / "data" / "sample_coding.csv",
        help="CSV/JSON file with excerpt_id, excerpt, coder_a, coder_b "
        "(default: bundled sample data)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="print a JSON summary instead of the text report",
    )
    args = parser.parse_args(argv)

    try:
        rows = load_coding_file(args.csv_path)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = summarize(rows)
    if args.json:
        out = {k: v for k, v in summary.items() if k != "confusion_matrix"}
        out["confusion_matrix"] = summary["confusion_matrix"].tolist()
        out["codes"] = summary["codes"]
        print(json.dumps(out, indent=2))
    else:
        print(f"File: {args.csv_path}")
        print(format_report(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
