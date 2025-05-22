import csv
import os
from typing import List, Dict, Any

class DataLoader:
    """
    Responsible for loading game data from external sources, like CSV files.
    """

    def __init__(self, data_folder_path: str = "data"):
        """
        Initializes the DataLoader.
        Args:
            data_folder_path (str): The path to the folder containing data files.
                                    Defaults to a 'data' directory in the project root.
        """
        # Get the absolute path to the project's root directory
        # This assumes the script running this (e.g., game.py) is in a subdirectory like 'src'
        # or the project root itself.
        # If game.py is in src/, __file__ of game.py is .../afk_quest/src/game.py
        # os.path.dirname(os.path.dirname(os.path.abspath(__file__))) would be afk_quest/
        # However, to make DataLoader more general, we'll assume it's instantiated
        # with a path relative to where the main script is run, or an absolute path.
        # For simplicity, we'll use a path relative to the current working directory.
        # This means the 'data' folder should be in the same directory from where
        # you run `python -m src.game`.
        self.base_data_path = os.path.abspath(data_folder_path)
        if not os.path.isdir(self.base_data_path):
            print(f"Warning: Data folder not found at {self.base_data_path}. "
                  f"Ensure it exists or specify the correct path.")


    def load_enemy_definitions(self, filename: str = "enemies.csv") -> List[Dict[str, Any]]:
        """
        Loads enemy definitions from a CSV file.
        The CSV file is expected to have headers: name,hp,attack_stat,loot_gold_min,loot_gold_max

        Args:
            filename (str): The name of the CSV file in the data folder.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents an enemy template. Returns an empty
                                  list if the file is not found or an error occurs.
        """
        enemy_templates: List[Dict[str, Any]] = []
        filepath = os.path.join(self.base_data_path, filename)

        if not os.path.exists(filepath):
            print(f"Error: Enemy definitions file not found at {filepath}")
            return enemy_templates

        try:
            with open(filepath, mode='r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or not all(key in reader.fieldnames for key in ['name', 'hp', 'attack_stat', 'loot_gold_min', 'loot_gold_max']):
                    print(f"Error: CSV file {filepath} is missing required headers: "
                          f"'name', 'hp', 'attack_stat', 'loot_gold_min', 'loot_gold_max'.")
                    return enemy_templates

                for row in reader:
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
                            print(f"Warning: Skipping row with empty name in {filepath}: {row}")
                            continue
                        if template["hp"] <= 0 or template["attack_stat"] < 0 or \
                           template["loot_gold_min"] < 0 or template["loot_gold_max"] < 0 or \
                           template["loot_gold_min"] > template["loot_gold_max"]:
                            print(f"Warning: Skipping row with invalid numeric values in {filepath}: {row}")
                            continue
                        enemy_templates.append(template)
                    except ValueError as ve:
                        print(f"Warning: Skipping row with invalid data type in {filepath}: {row}. Error: {ve}")
                    except KeyError as ke:
                        print(f"Warning: Skipping row with missing key in {filepath}: {row}. Error: {ke}")

        except FileNotFoundError:
            print(f"Error: File not found at {filepath}. Cannot load enemy definitions.")
        except Exception as e:
            print(f"An unexpected error occurred while loading {filepath}: {e}")

        if not enemy_templates:
            print(f"Warning: No valid enemy definitions loaded from {filepath}.")
        else:
            print(f"Successfully loaded {len(enemy_templates)} enemy definitions from {filepath}.")
        return enemy_templates

