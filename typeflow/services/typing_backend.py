import time
import random
import logging
import sys
import pyautogui

logger = logging.getLogger("TypeFlow")

# Windows ctypes SendInput declarations for robust Unicode typing
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    # Structure declarations for mouse/keyboard inputs
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    INPUT_KEYBOARD = 1

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD)
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
        ]

    class INPUT(ctypes.Structure):
        class _INPUT(ctypes.Union):
            _fields_ = [
                ("mi", MOUSEINPUT),
                ("ki", KEYBDINPUT),
                ("hi", HARDWAREINPUT)
            ]
        _fields_ = [("type", wintypes.DWORD), ("u", _INPUT)]

    SendInput = ctypes.windll.user32.SendInput
    SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    SendInput.restype = wintypes.UINT


class TypingBackend:
    def __init__(self):
        self._initialized = False

    def initialize(self) -> None:
        """Initializes the backend settings."""
        # Disable PyAutoGUI fail-safe to prevent crash, since we implement ESC emergency stop thread-safely
        pyautogui.FAILSAFE = False
        self._initialized = True
        logger.info("Typing backend initialized.")

    def cleanup(self) -> None:
        """Cleans up the backend resources."""
        self._initialized = False
        logger.info("Typing backend cleaned up.")

    def type_character(self, char: str) -> None:
        """Types a single character simulating keyboard input."""
        if not self._initialized:
            self.initialize()

        # Handle special key translations
        if char == "\n":
            self.press_enter()
            return
        elif char == "\t":
            self.press_key("tab")
            return
        elif char == "\r":
            # Ignore carriage returns to avoid double enters
            return

        # Attempt to use Windows SendInput for unicode support
        if IS_WINDOWS:
            try:
                self._send_unicode_char(char)
                return
            except Exception as e:
                logger.warning(f"Windows SendInput failed: {e}. Falling back to PyAutoGUI.")

        # Fallback to PyAutoGUI
        try:
            pyautogui.write(char)
        except Exception as e:
            logger.error(f"PyAutoGUI write failed: {e}")

    def press_key(self, key_name: str) -> None:
        """Presses a special action key (like 'tab', 'backspace')."""
        try:
            pyautogui.press(key_name)
        except Exception as e:
            logger.error(f"Failed to press key {key_name}: {e}")

    def press_enter(self) -> None:
        """Presses the enter key."""
        self.press_key("enter")

    def supports_unicode(self) -> bool:
        """Returns True if the backend supports Unicode (always True with ctypes on Windows)."""
        return IS_WINDOWS

    def _send_unicode_char(self, char: str) -> None:
        """Uses Win32 SendInput to type arbitrary unicode character."""
        # Convert char to UTF-16 code unit
        code_units = char.encode('utf-16-le')
        
        # UTF-16 characters can be 2 bytes (BMP) or 4 bytes (surrogate pairs)
        # We loop over two-byte units (WORDs)
        for i in range(0, len(code_units), 2):
            val = int.from_bytes(code_units[i:i+2], 'little')
            
            # Press key event
            ki_press = KEYBDINPUT(wVk=0, wScan=val, dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=None)
            input_press = INPUT(type=INPUT_KEYBOARD, u=INPUT._INPUT(ki=ki_press))
            res = SendInput(1, ctypes.byref(input_press), ctypes.sizeof(input_press))
            if res == 0:
                raise RuntimeError("SendInput press event failed")
            
            # Small sleep to ensure key processing
            time.sleep(0.001)
            
            # Release key event
            ki_release = KEYBDINPUT(wVk=0, wScan=val, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)
            input_release = INPUT(type=INPUT_KEYBOARD, u=INPUT._INPUT(ki=ki_release))
            res = SendInput(1, ctypes.byref(input_release), ctypes.sizeof(input_release))
            if res == 0:
                raise RuntimeError("SendInput release event failed")
            
            time.sleep(0.001)
