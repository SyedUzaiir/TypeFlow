from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from .enums import TypingState, Theme, TypingSpeed

@dataclass
class TypingSettings:
    delay_speed: str = "Medium"          # "Slow", "Medium", "Fast", "Custom"
    custom_delay_ms: int = 50
    countdown_seconds: int = 3
    press_enter: bool = False
    preserve_breaks: bool = True
    type_punctuation: bool = True
    randomize_delay: bool = False
    theme: str = "dark"
    version: int = 1

    def get_char_delay(self) -> float:
        """Returns character delay in seconds."""
        if self.delay_speed == "Slow":
            return 0.1
        elif self.delay_speed == "Medium":
            return 0.05
        elif self.delay_speed == "Fast":
            return 0.01
        else:
            return self.custom_delay_ms / 1000.0

@dataclass
class TypingSession:
    text: str
    total_chars: int
    current_index: int
    started_at: datetime
    state: TypingState
    settings: TypingSettings
    elapsed_seconds: int = 0

@dataclass
class RecoveryState:
    text: str
    current_index: int
    elapsed_seconds: int
    settings: TypingSettings
    queue_texts: List[str] = field(default_factory=list)

@dataclass
class TypingProgress:
    index: int
    total: int
    elapsed_seconds: int
    eta_seconds: int
    cpm: int
    previous_chars: str
    current_char: str
    remaining_chars: str
