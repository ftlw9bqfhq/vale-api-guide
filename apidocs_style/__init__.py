"""Lint API reference pages against the house style guide."""

from .checks import Issue, iter_documents, scan_file, scan_text
from .rules import RULES

__all__ = ["Issue", "RULES", "iter_documents", "scan_file", "scan_text"]
__version__ = "0.1.0"
