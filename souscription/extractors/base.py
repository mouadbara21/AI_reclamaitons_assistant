"""
Abstract base class for all document-specific extractors.
"""

from abc import ABC, abstractmethod
from souscription.models.document import ExtractedDocument


class BaseExtractor(ABC):
    """Base class for document field extractors.

    Every document-specific parser should inherit from this class and
    implement the `extract` method.  The base class provides shared
    helpers that are useful across multiple document types.
    """

    @abstractmethod
    def extract(self, text: str) -> ExtractedDocument:
        """Parse raw text and return a populated Pydantic model.

        Args:
            text: The full text content extracted from the document (either
                  via PyMuPDF or OCR).

        Returns:
            A concrete subclass of ExtractedDocument with all available
            fields populated.
        """
        ...

    # ── Shared helpers ──────────────────────────────────────────────

    @staticmethod
    def find_field_value(lines: list[str], anchor: str, skip_corrupt: bool = True,
                         max_lookahead: int = 3) -> str:
        """Find the value on the line(s) following an anchor label.

        Many Moroccan admin documents use a two-line layout:
            Label (anchor)
            Value

        This helper scans for the anchor and returns the first non-empty,
        non-corrupted line within `max_lookahead` lines after it.

        Args:
            lines: Pre-split, stripped lines of the document text.
            anchor: Case-sensitive substring to match in the label line.
            skip_corrupt: If True, skip lines containing Greek-block
                          corruption (U+0370–U+03FF).
            max_lookahead: How many lines after the anchor to scan.

        Returns:
            The extracted value string, or "" if not found.
        """
        for i, line in enumerate(lines):
            if anchor in line:
                for j in range(1, max_lookahead + 1):
                    if i + j < len(lines):
                        candidate = lines[i + j].strip()
                        if not candidate:
                            continue
                        if skip_corrupt and _has_greek_corruption(candidate):
                            continue
                        return candidate
                break
        return ""


def _has_greek_corruption(text: str) -> bool:
    """Detect corrupted PDF encoding (Greek block U+0370–U+03FF)."""
    return any(0x0370 <= ord(c) <= 0x03FF for c in text)
