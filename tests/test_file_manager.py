import pytest
import os
import json
from src.character import Character
from src import file_manager # Relative import

# Use pytest's tmp_path fixture for creating temporary files for tests
@pytest.fixture
def temp_char_file(tmp_path):
    return tmp_path / "test_char_save.json"

class TestFileManager:
    def test_save_character_creates_file(self, temp_char_file):
        char = Character(name="TestSave")
        file_manager.save_character(char, str(temp_char_file))
        assert os.path.exists(temp_char_file)
        with open(temp_char_file, 'r') as f:
            data = json.load(f)
            assert data["name"] == "TestSave"

    def test_load_character_returns_character_object(self, temp_char_file):
        char_data = {
            "name": "TestLoad", "level": 2, "current_experience": 5,
            "current_hp": 25, "gold": 50,
            "equipment": {"weapon": "Sword", "armour": None, "item": None}
        }
        with open(temp_char_file, 'w') as f:
            json.dump(char_data, f)

        loaded_char = file_manager.load_character(str(temp_char_file))
        assert isinstance(loaded_char, Character)
        assert loaded_char.name == "TestLoad"
        assert loaded_char.level == 2
        assert loaded_char.current_hp == 25
        assert loaded_char.equipment["weapon"] == "Sword"

    def test_load_character_returns_none_for_missing_file(self, tmp_path):
        missing_file = tmp_path / "non_existent_char.json"
        loaded_char = file_manager.load_character(str(missing_file))
        assert loaded_char is None

    def test_load_character_returns_none_for_corrupted_file(self, temp_char_file, capsys):
        with open(temp_char_file, 'w') as f:
            f.write("this is not valid json")

        loaded_char = file_manager.load_character(str(temp_char_file))
        assert loaded_char is None
        captured = capsys.readouterr()
        assert f"Error loading character from {str(temp_char_file)}" in captured.out


    def test_load_character_returns_none_for_missing_keys(self, temp_char_file, capsys):
        # Missing 'level' key
        char_data_missing_key = {
            "name": "TestIncomplete", "current_experience": 5,
            "current_hp": 25, "gold": 50,
            "equipment": {"weapon": "Sword", "armour": None, "item": None}
        }
        with open(temp_char_file, 'w') as f:
            json.dump(char_data_missing_key, f)

        loaded_char = file_manager.load_character(str(temp_char_file))
        assert loaded_char is None
        captured = capsys.readouterr()
        assert f"Save file {str(temp_char_file)} is missing required data" in captured.out


    def test_save_and_load_retains_data_integrity(self, temp_char_file):
        original_char = Character(
            name="IntegrityCheck", level=3, current_experience=12,
            gold=120, equipment={"weapon": "Axe", "armour": "Shield", "item": "Rope"}
        )
        original_char.take_damage(10) # current_hp should be (3*15 - 10) = 35

        file_manager.save_character(original_char, str(temp_char_file))
        loaded_char = file_manager.load_character(str(temp_char_file))

        assert loaded_char is not None
        assert loaded_char.name == original_char.name
        assert loaded_char.level == original_char.level
        assert loaded_char.current_experience == original_char.current_experience
        assert loaded_char.max_hp == original_char.max_hp
        assert loaded_char.current_hp == original_char.current_hp
        assert loaded_char.experience_to_next_level == original_char.experience_to_next_level
        assert loaded_char.gold == original_char.gold
        assert loaded_char.equipment == original_char.equipment
        assert loaded_char.is_dead == original_char.is_dead