class BaseOCRProvider:
    def extract_text(self, image_path: str) -> str:
        """Abstract method to run OCR on an image and return text."""
        raise NotImplementedError("OCR Providers must implement extract_text")
