import os
import json
from pathlib import Path
from typing import Optional, List
from core.models import RecoveryState, TypingSettings

class RecoveryManager:
    def __init__(self, filename: str = "recovery.json"):
        self.config_dir = Path.home() / ".typeflow"
        self.recovery_path = self.config_dir / filename

    def save_recovery(self, state: RecoveryState) -> None:
        """Saves current recovery state to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            settings = state.settings
            data = {
                "text": state.text,
                "current_index": state.current_index,
                "elapsed_seconds": state.elapsed_seconds,
                "queue_texts": state.queue_texts,
                "settings": {
                    "delay_speed": settings.delay_speed,
                    "custom_delay_ms": settings.custom_delay_ms,
                    "countdown_seconds": settings.countdown_seconds,
                    "press_enter": settings.press_enter,
                    "preserve_breaks": settings.preserve_breaks,
                    "type_punctuation": settings.type_punctuation,
                    "randomize_delay": settings.randomize_delay,
                    "theme": settings.theme
                }
            }
            with open(self.recovery_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def load_recovery(self) -> Optional[RecoveryState]:
        """Loads recovery state if it exists, otherwise returns None."""
        if not self.recovery_path.exists():
            return None

        try:
            with open(self.recovery_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            settings_data = data.get("settings", {})
            settings = TypingSettings(
                delay_speed=settings_data.get("delay_speed", "Medium"),
                custom_delay_ms=settings_data.get("custom_delay_ms", 50),
                countdown_seconds=settings_data.get("countdown_seconds", 3),
                press_enter=settings_data.get("press_enter", False),
                preserve_breaks=settings_data.get("preserve_breaks", True),
                type_punctuation=settings_data.get("type_punctuation", True),
                randomize_delay=settings_data.get("randomize_delay", False),
                theme=settings_data.get("theme", "dark")
            )

            return RecoveryState(
                text=data.get("text", ""),
                current_index=data.get("current_index", 0),
                elapsed_seconds=data.get("elapsed_seconds", 0),
                settings=settings,
                queue_texts=data.get("queue_texts", [])
            )
        except Exception:
            return None

    def clear_recovery(self) -> None:
        """Deletes recovery file when typing completes or is cancelled successfully."""
        try:
            if self.recovery_path.exists():
                self.recovery_path.unlink()
        except Exception:
            pass
