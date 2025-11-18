from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


class OcrPolicyDecider:
    """Decide whether to enable OCR for a given in-memory document."""

    def __init__(self, *, sample_pages: int = 5, char_threshold: int = 200) -> None:
        self.sample_pages = sample_pages
        self.char_threshold = char_threshold

    def should_ocr(self, *, filename: str, document_bytes: bytes) -> bool:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return self._should_ocr_pdf(document_bytes)
        # Non-PDF formats do not use this toggle; return False by default.
        return False

    def _should_ocr_pdf(self, document_bytes: bytes) -> bool:
        """
        Determine the need for OCR by sampling the PDF text layer.

        Pages with insufficient extracted characters are treated as scanned pages,
        so the pipeline falls back to OCR to recover text.
        """

        try:
            reader = PdfReader(BytesIO(document_bytes))
        except Exception:
            return True

        num_pages = len(reader.pages)
        if num_pages == 0:
            return True

        pages_to_check = min(self.sample_pages, num_pages)
        total_chars = 0
        checked = 0
        for i in range(pages_to_check):
            try:
                text = reader.pages[i].extract_text() or ""
            except Exception:
                text = ""
            total_chars += len(text.strip())
            checked += 1

        if checked == 0:
            return True

        avg_chars = total_chars / checked
        return avg_chars < self.char_threshold


__all__ = ["OcrPolicyDecider"]
