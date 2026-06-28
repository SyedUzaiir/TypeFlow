import sys
import time
import logging
from services.typing_backend import TypingBackend

# Configure logging to console
logging.basicConfig(level=logging.DEBUG)

def main():
    print("Testing TypingBackend in 3 seconds...")
    print("Please focus Notepad or another text input area now!")
    time.sleep(3)
    
    backend = TypingBackend()
    backend.initialize()
    
    test_string = "Hello from TypeFlow Unicode Test! (12345)\n"
    
    # Use ASCII representation for console logging safety
    print("Typing test string...")
    
    for char in test_string:
        backend.type_character(char)
        time.sleep(0.05)
        
    backend.cleanup()
    print("Test finished.")

if __name__ == "__main__":
    main()
