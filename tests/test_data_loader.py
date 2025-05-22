import pytest
import os
import csv
from src.data_loader import DataLoader

@pytest.fixture
def temp_data_dir(tmp_path):
    """Creates a temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def valid_enemies_csv_file(temp_data_dir):
    """Creates a valid enemies.csv file in the temporary data directory."""
    filepath = temp_data_dir / "enemies_good.csv"
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "hp", "attack_stat", "loot_gold_min", "loot_gold_max"])
        writer.writerow(["TestGoblin", "10", "2", "1", "3"])
        writer.writerow(["TestOgre", "50", "8", "10", "20"])
    return filepath

@pytest.fixture
def empty_enemies_csv_file(temp_data_dir):
    """Creates an empty enemies.csv file (only headers)."""
    filepath = temp_data_dir / "enemies_empty.csv"
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "hp", "attack_stat", "loot_gold_min", "loot_gold_max"])
    return filepath

@pytest.fixture
def malformed_enemies_csv_file(temp_data_dir):
    """Creates a malformed enemies.csv file (bad data type)."""
    filepath = temp_data_dir / "enemies_malformed.csv"
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "hp", "attack_stat", "loot_gold_min", "loot_gold_max"])
        writer.writerow(["BadDragon", "very_high", "lots", "some", "many"]) # bad types
        writer.writerow(["GoodSlime", "5", "1", "0", "1"])
    return filepath

@pytest.fixture
def missing_header_csv_file(temp_data_dir):
    """Creates a CSV file with missing headers."""
    filepath = temp_data_dir / "enemies_no_header.csv"
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "hp", "attack_stat"]) # Missing loot headers
        writer.writerow(["NoLootGoblin", "10", "2"])
    return filepath


class TestDataLoader:
    def test_load_enemy_definitions_valid_file(self, valid_enemies_csv_file):
        # DataLoader expects to find 'data' in the CWD, or path specified.
        # For testing, we point it to the parent of the specific temp file.
        loader = DataLoader(data_folder_path=str(valid_enemies_csv_file.parent))
        definitions = loader.load_enemy_definitions(filename=valid_enemies_csv_file.name)
        assert len(definitions) == 2
        assert definitions[0]["name"] == "TestGoblin"
        assert definitions[0]["hp"] == 10
        assert definitions[1]["name"] == "TestOgre"
        assert definitions[1]["loot_gold_max"] == 20

    def test_load_enemy_definitions_file_not_found(self, temp_data_dir, capsys):
        loader = DataLoader(data_folder_path=str(temp_data_dir))
        definitions = loader.load_enemy_definitions(filename="non_existent.csv")
        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Error: Enemy definitions file not found" in captured.out

    def test_load_enemy_definitions_empty_file(self, empty_enemies_csv_file, capsys):
        loader = DataLoader(data_folder_path=str(empty_enemies_csv_file.parent))
        definitions = loader.load_enemy_definitions(filename=empty_enemies_csv_file.name)
        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Warning: No valid enemy definitions loaded" in captured.out

    def test_load_enemy_definitions_malformed_data(self, malformed_enemies_csv_file, capsys):
        loader = DataLoader(data_folder_path=str(malformed_enemies_csv_file.parent))
        definitions = loader.load_enemy_definitions(filename=malformed_enemies_csv_file.name)
        assert len(definitions) == 1 # Only GoodSlime should load
        assert definitions[0]["name"] == "GoodSlime"
        captured = capsys.readouterr()
        assert "Warning: Skipping row with invalid data type" in captured.out

    def test_load_enemy_definitions_missing_headers(self, missing_header_csv_file, capsys):
        loader = DataLoader(data_folder_path=str(missing_header_csv_file.parent))
        definitions = loader.load_enemy_definitions(filename=missing_header_csv_file.name)
        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Error: CSV file" in captured.out and "is missing required headers" in captured.out

    def test_data_loader_nonexistent_data_folder(self, tmp_path, capsys):
        non_existent_folder = tmp_path / "non_existent_data_folder"
        loader = DataLoader(data_folder_path=str(non_existent_folder))
        # This should print a warning during __init__
        captured = capsys.readouterr() # Capture prints from __init__
        assert f"Warning: Data folder not found at {str(non_existent_folder)}" in captured.out
        # Attempting to load should also fail gracefully
        definitions = loader.load_enemy_definitions(filename="any.csv")
        assert len(definitions) == 0
        captured = capsys.readouterr() # Capture prints from load method
        assert "Error: Enemy definitions file not found" in captured.out

