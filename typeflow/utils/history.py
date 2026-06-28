import os
import json
from pathlib import Path
from typing import List

class HistoryManager:
    def __init__(self, filename: str = "history.json", max_items: int = 10):
        self.config_dir = Path.home() / ".typeflow"
        self.history_path = self.config_dir / filename
        self.max_items = max_items

    def load_history(self) -> List[str]:
        """Loads and returns history items."""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [item for item in data if isinstance(item, str) and item.strip()]
        except Exception:
            pass
        return []

    def save_history(self, history: List[str]) -> None:
        """Saves current history items to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Remove duplicates while preserving order
            cleaned = []
            for item in history:
                cleaned_item = item.strip()
                if cleaned_item and cleaned_item not in cleaned:
                    cleaned.append(cleaned_item)
            
            # Trim
            trimmed = cleaned[:self.max_items]
            
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, indent=4)
        except Exception:
            pass

    def add_item(self, text: str) -> None:
        """Adds a new text block to the top of the history list."""
        text = text.strip()
        if not text:
            return
        
        history = self.load_history()
        
        # Remove if already exists to push to front
        if text in history:
            history.remove(text)
            
        history.insert(0, text)
        self.save_history(history)

    def clear(self) -> None:
        """Clears all history."""
        self.save_history([])
