import os
import json
import pytest
from pathlib import Path
from core.models import TypingSettings, RecoveryState, TypingProgress
from core.enums import TypingSpeed
from utils.settings import SettingsManager
from utils.recovery import RecoveryManager
from utils.history import HistoryManager

# Mock/Test paths inside local temp directory to avoid dirtying user config files
TEST_DIR = Path("./temp_test_typeflow")

def clean_directory_recursive(path: Path) -> None:
    if not path.exists():
        return
    for item in path.iterdir():
        if item.is_dir():
            clean_directory_recursive(item)
            try:
                item.rmdir()
            except Exception:
                pass
        else:
            try:
                item.unlink()
            except Exception:
                pass

@pytest.fixture(autouse=True)
def setup_teardown():
    # Clean up test directory files recursively before test starts
    clean_directory_recursive(TEST_DIR)
    # Setup test directory
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Clean up test directory files recursively after test ends
    clean_directory_recursive(TEST_DIR)
    try:
        if TEST_DIR.exists():
            TEST_DIR.rmdir()
    except Exception:
        pass

def test_typing_settings_delay():
    """Verify that settings correctly return expected delay mappings."""
    s_slow = TypingSettings(delay_speed="Slow")
    assert s_slow.get_char_delay() == 0.1
    
    s_medium = TypingSettings(delay_speed="Medium")
    assert s_medium.get_char_delay() == 0.05
    
    s_fast = TypingSettings(delay_speed="Fast")
    assert s_fast.get_char_delay() == 0.01
    
    s_custom = TypingSettings(delay_speed="Custom", custom_delay_ms=250)
    assert s_custom.get_char_delay() == 0.25

def test_settings_manager_load_save(monkeypatch):
    """Test loading and saving settings via SettingsManager."""
    # Monkeypatch home directory to point to our test folder
    monkeypatch.setattr(Path, "home", lambda: TEST_DIR)
    
    manager = SettingsManager(filename="test_settings.json")
    
    # Check default initialization
    assert manager.settings.delay_speed == "Medium"
    assert manager.settings.theme == "dark"
    
    # Make a modification
    manager.settings.delay_speed = "Slow"
    manager.settings.theme = "light"
    manager.settings.custom_delay_ms = 120
    manager.save()
    
    # Reload from file
    new_manager = SettingsManager(filename="test_settings.json")
    assert new_manager.settings.delay_speed == "Slow"
    assert new_manager.settings.theme == "light"
    assert new_manager.settings.custom_delay_ms == 120

def test_recovery_manager_checkpoint(monkeypatch):
    """Test saving and loading recovery states."""
    monkeypatch.setattr(Path, "home", lambda: TEST_DIR)
    
    manager = RecoveryManager(filename="test_recovery.json")
    
    settings = TypingSettings(delay_speed="Fast", press_enter=True)
    state = RecoveryState(
        text="Hello World",
        current_index=6,
        elapsed_seconds=12,
        settings=settings,
        queue_texts=["Queue Item 1", "Queue Item 2"]
    )
    
    manager.save_recovery(state)
    
    loaded = manager.load_recovery()
    assert loaded is not None
    assert loaded.text == "Hello World"
    assert loaded.current_index == 6
    assert loaded.elapsed_seconds == 12
    assert loaded.settings.delay_speed == "Fast"
    assert loaded.settings.press_enter is True
    assert loaded.queue_texts == ["Queue Item 1", "Queue Item 2"]
    
    # Test clearing recovery
    manager.clear_recovery()
    assert manager.load_recovery() is None

def test_history_manager_dedup(monkeypatch):
    """Verify history limits, ordering, and deduplication works."""
    monkeypatch.setattr(Path, "home", lambda: TEST_DIR)
    
    manager = HistoryManager(filename="test_history.json", max_items=4)
    
    manager.add_item("Text A")
    manager.add_item("Text B")
    manager.add_item("Text A")  # Duplicate, should bring to front
    manager.add_item("Text C")
    manager.add_item("Text D")
    manager.add_item("Text E")  # Exceeds max items (4)
    
    history = manager.load_history()
    # Expected order: Text E, Text D, Text C, Text A
    # (Text B dropped because E, D, C, A fill the max limit of 4 items)
    assert len(history) == 4
    assert history[0] == "Text E"
    assert history[1] == "Text D"
    assert history[2] == "Text C"
    assert history[3] == "Text A"
