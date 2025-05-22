import pytest
import os
import csv
import configparser # Keep for type hinting and creating real objects in helpers if needed
from unittest.mock import patch, MagicMock, mock_open # mock_open can be useful for file reads
import requests # Ensure requests is imported for requests.exceptions
from src.data_loader import DataLoader

# --- Fixtures for CSV content (remains the same) ---
VALID_CSV_CONTENT = """name,hp,attack_stat,loot_gold_min,loot_gold_max
TestGoblin,10,2,1,3
TestOgre,50,8,10,20
"""
EMPTY_CSV_CONTENT_WITH_HEADER = "name,hp,attack_stat,loot_gold_min,loot_gold_max\n"
MALFORMED_CSV_CONTENT = """name,hp,attack_stat,loot_gold_min,loot_gold_max
BadDragon,very_high,lots,some,many
GoodSlime,5,1,0,1
"""
MISSING_HEADER_CSV_CONTENT = """name,hp,attack_stat
NoLootGoblin,10,2
"""

# --- Helper to configure the MOCKED ConfigParser INSTANCE ---
def configure_mock_config_instance(mock_config_obj: MagicMock, google_url: str = "", local_fallback: str = "enemies.csv", has_section_val: bool = True):
    """
    Configures a MagicMock object to behave like a ConfigParser instance.
    """
    def get_side_effect(section, option, fallback=None):
        if section == "DataSources.Enemies":
            if option == "google_sheet_url":
                return google_url
            if option == "local_csv_fallback":
                return local_fallback
        return fallback

    mock_config_obj.has_section.return_value = has_section_val
    mock_config_obj.get.side_effect = get_side_effect
    mock_config_obj.read.return_value = None # Mock read to do nothing

@pytest.fixture
def temp_data_dir(tmp_path):
    data_dir = tmp_path / "test_data_files"
    data_dir.mkdir()
    mock_config_path = tmp_path / "dummy_config.ini" 
    return data_dir, mock_config_path


class TestDataLoader:

    @patch('src.data_loader.os.path.exists') # Mock os.path.exists
    @patch('src.data_loader.requests.get')
    @patch('src.data_loader.configparser.ConfigParser') # Mocks the ConfigParser CLASS
    def test_load_from_google_sheet_success(self, MockConfigParserClass, mock_requests_get, mock_os_exists, temp_data_dir):
        data_dir, mock_config_path_for_init = temp_data_dir
        
        # Ensure _load_config believes the config file exists so it uses the mocked ConfigParser
        mock_os_exists.return_value = True 

        mock_config_instance = MockConfigParserClass.return_value 
        configure_mock_config_instance(mock_config_instance, google_url="http://fakegooglesheet.com/export.csv")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = VALID_CSV_CONTENT
        mock_response.headers = {'content-type': 'text/csv'}
        mock_requests_get.return_value = mock_response

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()

        assert len(definitions) == 2
        assert definitions[0]["name"] == "TestGoblin"
        mock_requests_get.assert_called_once_with("http://fakegooglesheet.com/export.csv", timeout=10)
        # Check that os.path.exists was called for the config file path
        mock_os_exists.assert_any_call(str(mock_config_path_for_init))

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.requests.get')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_from_local_csv_fallback_on_sheet_failure(self, MockConfigParserClass, mock_requests_get, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        local_csv_name = "fallback_enemies.csv"
        fallback_csv_path = data_dir / local_csv_name
        with open(fallback_csv_path, 'w') as f:
            f.write(VALID_CSV_CONTENT)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True # Config file "exists"
            if path_arg == str(fallback_csv_path): return True # Fallback CSV "exists"
            return False 
        mock_os_exists.side_effect = os_exists_side_effect
        
        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(
            mock_config_instance,
            google_url="http://brokenurl.com/export.csv", 
            local_fallback=local_csv_name
        )

        mock_requests_get.side_effect = requests.exceptions.RequestException("Network Error")

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()

        assert len(definitions) == 2
        assert definitions[0]["name"] == "TestGoblin"
        captured = capsys.readouterr()
        assert "Error fetching enemy definitions from Google Sheet" in captured.out
        assert f"Successfully loaded 2 enemy definitions from: Local CSV ({str(fallback_csv_path)})" in captured.out

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_from_local_csv_no_google_url_configured(self, MockConfigParserClass, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        local_csv_name = "local_only_enemies.csv"
        local_csv_path = data_dir / local_csv_name
        with open(local_csv_path, 'w') as f:
            f.write(VALID_CSV_CONTENT)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True
            if path_arg == str(local_csv_path): return True
            return False
        mock_os_exists.side_effect = os_exists_side_effect

        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(mock_config_instance, google_url="", local_fallback=local_csv_name)

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()

        assert len(definitions) == 2
        assert definitions[0]["name"] == "TestGoblin" # Corrected: VALID_CSV_CONTENT starts with TestGoblin
        captured = capsys.readouterr()
        assert "No Google Sheet URL configured" in captured.out or "Google Sheet URL in config was present but invalid" in captured.out
        assert f"Successfully loaded 2 enemy definitions from: Local CSV ({str(local_csv_path)})" in captured.out

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.requests.get')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_local_csv_file_not_found_after_sheet_fail(self, MockConfigParserClass, mock_requests_get, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        
        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True # Config file "exists"
            # Fallback CSV does not exist
            if "non_existent_fallback.csv" in str(path_arg): return False 
            return False # Default to false for other unexpected paths
        mock_os_exists.side_effect = os_exists_side_effect

        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(
            mock_config_instance,
            google_url="http://anotherbrokenurl.com/export.csv",
            local_fallback="non_existent_fallback.csv"
        )
        mock_requests_get.side_effect = requests.exceptions.RequestException("Network Error")

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()

        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Error fetching enemy definitions from Google Sheet" in captured.out
        assert "Local fallback enemy definitions file not found" in captured.out
        assert "Critical Warning: No enemy definitions loaded" in captured.out

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_empty_local_csv_file(self, MockConfigParserClass, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        empty_csv_name = "empty_enemies.csv"
        empty_csv_path = data_dir / empty_csv_name
        with open(empty_csv_path, 'w') as f:
            f.write(EMPTY_CSV_CONTENT_WITH_HEADER)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True
            if path_arg == str(empty_csv_path): return True
            return False
        mock_os_exists.side_effect = os_exists_side_effect

        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(mock_config_instance, google_url="", local_fallback=empty_csv_name)

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()
        
        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Successfully loaded 0 enemy definitions" in captured.out or \
               "Critical Warning: No enemy definitions loaded" in captured.out

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_malformed_local_csv_data(self, MockConfigParserClass, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        malformed_csv_name = "malformed_enemies.csv"
        malformed_csv_path = data_dir / malformed_csv_name
        with open(malformed_csv_path, 'w') as f:
            f.write(MALFORMED_CSV_CONTENT)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True
            if path_arg == str(malformed_csv_path): return True
            return False
        mock_os_exists.side_effect = os_exists_side_effect

        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(mock_config_instance, google_url="", local_fallback=malformed_csv_name)

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()
        
        assert len(definitions) == 1 
        assert definitions[0]["name"] == "GoodSlime"
        captured = capsys.readouterr()
        assert "Warning: Skipping row" in captured.out
        assert "invalid data type" in captured.out

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_load_local_csv_missing_headers(self, MockConfigParserClass, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        missing_header_csv_name = "missing_header.csv"
        missing_header_csv_path = data_dir / missing_header_csv_name
        with open(missing_header_csv_path, 'w') as f:
            f.write(MISSING_HEADER_CSV_CONTENT)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True
            if path_arg == str(missing_header_csv_path): return True
            return False
        mock_os_exists.side_effect = os_exists_side_effect

        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(mock_config_instance, google_url="", local_fallback=missing_header_csv_name)

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()
        
        assert len(definitions) == 0
        captured = capsys.readouterr()
        assert "Error: CSV data from" in captured.out and "is missing required headers" in captured.out

    @patch('src.data_loader.os.path.isdir') 
    @patch('src.data_loader.os.path.exists') 
    def test_data_loader_nonexistent_config_file_warning(self, mock_os_path_exists_for_config, mock_os_path_isdir_for_data, tmp_path, capsys):
        mock_os_path_isdir_for_data.return_value = True 
        
        non_existent_config_file = tmp_path / "truly_non_existent_config.ini"
        mock_os_path_exists_for_config.side_effect = lambda p: False if p == str(non_existent_config_file) else True

        loader = DataLoader(data_folder_path=str(tmp_path), config_filepath=str(non_existent_config_file))
        captured_init = capsys.readouterr()
        
        expected_abs_config_path = os.path.abspath(str(non_existent_config_file))
        assert f"Warning: Configuration file not found at {expected_abs_config_path}" in captured_init.out

        definitions = loader.load_enemy_definitions()
        assert len(definitions) == 0
        captured_load = capsys.readouterr()
        assert "No Google Sheet URL configured" in captured_load.out 
        assert "No local CSV fallback configured" in captured_load.out
        assert "Critical Warning: No enemy definitions loaded" in captured_load.out
        mock_os_path_exists_for_config.assert_any_call(str(non_existent_config_file))

    @patch('src.data_loader.os.path.exists')
    @patch('src.data_loader.requests.get')
    @patch('src.data_loader.configparser.ConfigParser')
    def test_google_sheet_http_error_fallback(self, MockConfigParserClass, mock_requests_get, mock_os_exists, temp_data_dir, capsys):
        data_dir, mock_config_path_for_init = temp_data_dir
        local_csv_name = "fallback_good.csv"
        fallback_csv_path = data_dir / local_csv_name
        with open(fallback_csv_path, 'w') as f:
            f.write(VALID_CSV_CONTENT)

        def os_exists_side_effect(path_arg):
            if path_arg == str(mock_config_path_for_init): return True
            if path_arg == str(fallback_csv_path): return True
            return False
        mock_os_exists.side_effect = os_exists_side_effect
        
        mock_config_instance = MockConfigParserClass.return_value
        configure_mock_config_instance(
            mock_config_instance,
            google_url="http://errorurl.com/export.csv",
            local_fallback=local_csv_name
        )
        
        mock_response_error = MagicMock()
        mock_response_error.status_code = 404
        mock_response_error.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_requests_get.return_value = mock_response_error

        loader = DataLoader(data_folder_path=str(data_dir), config_filepath=str(mock_config_path_for_init))
        definitions = loader.load_enemy_definitions()

        assert len(definitions) == 2
        assert definitions[0]["name"] == "TestGoblin"
        captured = capsys.readouterr()
        assert "Error fetching enemy definitions from Google Sheet" in captured.out
        assert "404 Client Error" in captured.out
        assert f"Successfully loaded 2 enemy definitions from: Local CSV ({str(fallback_csv_path)})" in captured.out

