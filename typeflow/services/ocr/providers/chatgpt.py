from services.ocr.base import BaseOCRProvider

class ChatGPTOCRProvider(BaseOCRProvider):
    def extract_text(self, image_path: str) -> str:
        """Stub for Vision/ChatGPT extraction."""
        return "[ChatGPT Vision OCR stub text extracted]"
