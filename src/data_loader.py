import csv
import os
import requests # For fetching from URL
import io # For StringIO to treat string as file
import configparser # For reading .ini config files
from typing import List, Dict, Any, Optional

class DataLoader:
    """
    Responsible for loading game data from external sources,
    like Google Sheets or local CSV files, based on a configuration file.
    """

    def __init__(self, data_folder_path: str = "data", config_filepath: str = "config.ini"):
        """
        Initializes the DataLoader.
        Args:
            data_folder_path (str): The path to the folder containing local data files.
            config_filepath (str): The path to the configuration file.
        """
        self.base_data_path = os.path.abspath(data_folder_path)
        self.config_filepath = os.path.abspath(config_filepath)
        self.config = self._load_config()

        if not os.path.isdir(self.base_data_path):
            print(f"Warning: Local data folder not found at {self.base_data_path}. "
                  f"Ensure it exists if fallback to local files is needed.")

    def _load_config(self) -> configparser.ConfigParser:
        """Loads the configuration from the .ini file."""
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_filepath):
            print(f"Warning: Configuration file not found at {self.config_filepath}. "
                  "DataLoader will rely on default behaviors or fail to find sources.")
            return config # Return empty config

        try:
            config.read(self.config_filepath)
        except configparser.Error as e:
            print(f"Error reading configuration file {self.config_filepath}: {e}")
            # Return an empty config or handle as a critical error
        return config

    def _parse_csv_data(self, csv_content_stream: io.TextIOBase, source_description: str) -> List[Dict[str, Any]]:
        """
        Parses CSV data from a given text stream (like a file or StringIO).

        Args:
            csv_content_stream (io.TextIOBase): A text stream containing CSV data.
            source_description (str): A description of the data source (e.g., file path or URL) for logging.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents an enemy template.
        """
        enemy_templates: List[Dict[str, Any]] = []
        try:
            # Sniff to check for header, though DictReader implies one
            # dialect = csv.Sniffer().sniff(csv_content_stream.read(1024))
            # csv_content_stream.seek(0) # Reset stream position after sniffing
            # reader = csv.DictReader(csv_content_stream, dialect=dialect)
            reader = csv.DictReader(csv_content_stream)

            required_headers = ['name', 'hp', 'attack_stat', 'loot_gold_min', 'loot_gold_max']
            if not reader.fieldnames or not all(key in reader.fieldnames for key in required_headers):
                print(f"Error: CSV data from {source_description} is missing required headers: "
                      f"{', '.join(required_headers)}. Found headers: {reader.fieldnames}")
                return enemy_templates

            for i, row in enumerate(reader):
                try:
                    template = {
                        "name": str(row["name"]).strip(),
                        "hp": int(row["hp"]),
                        "attack_stat": int(row["attack_stat"]),
                        "loot_gold_min": int(row["loot_gold_min"]),
                        "loot_gold_max": int(row["loot_gold_max"]),
                    }
                    # Basic validation
                    if not template["name"]:
                        print(f"Warning: Skipping row {i+1} with empty name in {source_description}: {row}")
                        continue
                    if template["hp"] <= 0 or template["attack_stat"] < 0 or \
                       template["loot_gold_min"] < 0 or template["loot_gold_max"] < 0 or \
                       template["loot_gold_min"] > template["loot_gold_max"]:
                        print(f"Warning: Skipping row {i+1} with invalid numeric values in {source_description}: {row}")
                        continue
                    enemy_templates.append(template)
                except ValueError as ve:
                    print(f"Warning: Skipping row {i+1} with invalid data type in {source_description}: {row}. Error: {ve}")
                except KeyError as ke:
                    print(f"Warning: Skipping row {i+1} with missing key in {source_description}: {row}. Error: {ke}")
        except csv.Error as ce:
            print(f"CSV Error while processing data from {source_description}: {ce}")
        except Exception as e:
            print(f"An unexpected error occurred while parsing CSV from {source_description}: {e}")
        return enemy_templates


    def load_enemy_definitions(self) -> List[Dict[str, Any]]:
        """
        Loads enemy definitions, trying the Google Sheet URL from config first,
        then falling back to a local CSV file if specified and the primary source fails.
        """
        enemy_templates: List[Dict[str, Any]] = []
        source_used = "None"

        google_sheet_url: Optional[str] = None
        local_csv_fallback: Optional[str] = None

        if self.config.has_section("DataSources.Enemies"):
            google_sheet_url = self.config.get("DataSources.Enemies", "google_sheet_url", fallback=None)
            local_csv_fallback = self.config.get("DataSources.Enemies", "local_csv_fallback", fallback=None)

        # Try Google Sheet first
        if google_sheet_url:
            print(f"Attempting to load enemy definitions from Google Sheet: {google_sheet_url}")
            try:
                response = requests.get(google_sheet_url, timeout=10) # 10 second timeout
                response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
                
                # Ensure content type is CSV-like, though Google export URLs should be fine
                content_type = response.headers.get('content-type', '').lower()
                if 'csv' not in content_type and 'text/plain' not in content_type: # text/plain can sometimes be used for CSV
                    print(f"Warning: Content type from Google Sheet URL is not CSV ({content_type}). Attempting to parse anyway.")

                # Use StringIO to treat the string response content like a file
                csv_content_stream = io.StringIO(response.text, newline='')
                enemy_templates = self._parse_csv_data(csv_content_stream, google_sheet_url)
                if enemy_templates:
                    source_used = f"Google Sheet ({google_sheet_url})"
            except requests.exceptions.RequestException as e:
                print(f"Error fetching enemy definitions from Google Sheet ({google_sheet_url}): {e}")
            except Exception as e: # Catch other potential errors during processing
                print(f"An unexpected error occurred while processing Google Sheet data: {e}")
        else:
            print("No Google Sheet URL configured for enemy definitions.")

        # If Google Sheet failed or wasn't specified, try local fallback
        if not enemy_templates and local_csv_fallback:
            print(f"Primary source failed or not specified. Attempting fallback to local CSV: {local_csv_fallback}")
            filepath = os.path.join(self.base_data_path, local_csv_fallback)
            if not os.path.exists(filepath):
                print(f"Error: Local fallback enemy definitions file not found at {filepath}")
            else:
                try:
                    with open(filepath, mode='r', encoding='utf-8', newline='') as file:
                        enemy_templates = self._parse_csv_data(file, filepath)
                    if enemy_templates:
                        source_used = f"Local CSV ({filepath})"
                except Exception as e:
                    print(f"An unexpected error occurred while loading local fallback {filepath}: {e}")
        elif not enemy_templates and not local_csv_fallback:
            print("No local CSV fallback configured for enemy definitions.")


        if not enemy_templates:
            print("Critical Warning: No enemy definitions loaded from any source.")
        else:
            print(f"Successfully loaded {len(enemy_templates)} enemy definitions from: {source_used}.")
        return enemy_templates

