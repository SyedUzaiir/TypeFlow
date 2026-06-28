import os
import json
from pathlib import Path
from core.models import TypingSettings

class SettingsManager:
    def __init__(self, filename: str = "settings.json"):
        # Put config in home directory .typeflow folder
        self.config_dir = Path.home() / ".typeflow"
        self.config_path = self.config_dir / filename
        self.settings = TypingSettings()
        self.load()

    def get_defaults(self) -> dict:
        return {
            "version": 1,
            "theme": "dark",
            "typing": {
                "delay_speed": "Medium",
                "custom_delay_ms": 50,
                "countdown_seconds": 3,
                "press_enter": False,
                "preserve_breaks": True,
                "type_punctuation": True,
                "randomize_delay": False
            },
            "window": {
                "width": 1000,
                "height": 650,
                "x": -1,
                "y": -1
            }
        }

    def load(self) -> None:
        """Loads settings from the JSON file. Defaults are loaded if file not found or corrupted."""
        if not self.config_path.exists():
            self.settings = TypingSettings()
            return

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Verify version
            version = data.get("version", 1)
            
            # Map values
            typing_data = data.get("typing", {})
            self.settings = TypingSettings(
                delay_speed=typing_data.get("delay_speed", "Medium"),
                custom_delay_ms=typing_data.get("custom_delay_ms", 50),
                countdown_seconds=typing_data.get("countdown_seconds", 3),
                press_enter=typing_data.get("press_enter", False),
                preserve_breaks=typing_data.get("preserve_breaks", True),
                type_punctuation=typing_data.get("type_punctuation", True),
                randomize_delay=typing_data.get("randomize_delay", False),
                theme=data.get("theme", "dark"),
                version=version
            )
            
            # Keep window configuration separate
            self.window_config = data.get("window", {"width": 1000, "height": 650, "x": -1, "y": -1})
        except Exception:
            # Revert to default in case of error
            self.settings = TypingSettings()
            self.window_config = {"width": 1000, "height": 650, "x": -1, "y": -1}

    def save(self) -> None:
        """Saves current settings and window coordinates to the JSON file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            window_data = getattr(self, "window_config", {"width": 1000, "height": 650, "x": -1, "y": -1})
            
            data = {
                "version": self.settings.version,
                "theme": self.settings.theme,
                "typing": {
                    "delay_speed": self.settings.delay_speed,
                    "custom_delay_ms": self.settings.custom_delay_ms,
                    "countdown_seconds": self.settings.countdown_seconds,
                    "press_enter": self.settings.press_enter,
                    "preserve_breaks": self.settings.preserve_breaks,
                    "type_punctuation": self.settings.type_punctuation,
                    "randomize_delay": self.settings.randomize_delay
                },
                "window": window_data
            }
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass # Suppress settings saving exception

    def get_window_geometry(self) -> tuple[int, int, int, int]:
        """Returns x, y, width, height."""
        config = getattr(self, "window_config", {"width": 1000, "height": 650, "x": -1, "y": -1})
        return (
            config.get("x", -1),
            config.get("y", -1),
            config.get("width", 1000),
            config.get("height", 650)
        )

    def set_window_geometry(self, x: int, y: int, width: int, height: int) -> None:
        self.window_config = {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
        self.save()
