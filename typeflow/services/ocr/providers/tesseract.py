from services.ocr.base import BaseOCRProvider

class TesseractOCRProvider(BaseOCRProvider):
    def extract_text(self, image_path: str) -> str:
        """Stub for Tesseract engine extraction."""
        return "[Tesseract OCR stub text extracted]"
