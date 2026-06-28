from enum import Enum, auto

class Theme(Enum):
    DARK = "dark"
    LIGHT = "light"

class TypingSpeed(Enum):
    SLOW = "Slow"
    MEDIUM = "Medium"
    FAST = "Fast"
    CUSTOM = "Custom"

class TypingState(Enum):
    READY = "Ready"
    COUNTDOWN = "Countdown"
    TYPING = "Typing"
    PAUSED = "Paused"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
