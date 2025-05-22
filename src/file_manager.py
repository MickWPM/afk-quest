import json
import os
from .character import Character # Use relative import

DEFAULT_SAVE_FILENAME = "character_data.json"

def save_character(character: Character, filepath: str = DEFAULT_SAVE_FILENAME):
    """Saves character object to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(character.to_dict(), f, indent=4)
        print(f"Character '{character.name}' saved to {filepath}.")
    except IOError as e:
        print(f"Error saving character: {e}")

def load_character(filepath: str = DEFAULT_SAVE_FILENAME) -> Character | None:
    """
    Loads character data from a JSON file.
    Returns None if the file doesn't exist or data is invalid.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Basic validation for essential keys
            required_keys = ["name", "level", "current_experience", "current_hp", "gold", "equipment"]
            if not all(key in data for key in required_keys):
                print(f"Error: Save file {filepath} is missing required data.")
                return None
            return Character.from_dict(data)
    except (IOError, json.JSONDecodeError, TypeError) as e: # Added TypeError for bad data
        print(f"Error loading character from {filepath}: {e}")
        # Optionally, you might want to delete or rename the corrupted file here
        return None