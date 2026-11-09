"""qual-coder-reliability: inter-coder reliability for qualitative coding."""

from .kappa import (
    cohens_kappa,
    confusion_matrix,
    expected_agreement,
    interpret_kappa,
    percent_agreement,
)
from .loader import load_coding_file, load_csv, load_json
from .report import disagreements, format_report, per_code_report, summarize

__all__ = [
    "cohens_kappa",
    "percent_agreement",
    "expected_agreement",
    "confusion_matrix",
    "interpret_kappa",
    "load_csv",
    "load_json",
    "load_coding_file",
    "per_code_report",
    "disagreements",
    "summarize",
    "format_report",
]

__version__ = "0.1.0"
