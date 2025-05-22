import random
from typing import List, Dict, Any, Optional
from .enemy import Enemy # Relative import

class EnemyManager:
    """
    Manages enemy templates and provides enemy instances for encounters.
    """
    def __init__(self, enemy_templates: List[Dict[str, Any]]):
        """
        Initializes the EnemyManager with a list of enemy templates.

        Args:
            enemy_templates (List[Dict[str, Any]]): A list of dictionaries,
                where each dictionary defines an enemy type. Expected keys are:
                "name", "hp", "attack_stat", "loot_gold_min", "loot_gold_max".
        """
        self.enemy_templates: List[Dict[str, Any]] = enemy_templates
        if not self.enemy_templates:
            print("Warning: EnemyManager initialized with no enemy templates.")

    def get_random_enemy(self) -> Optional[Enemy]:
        """
        Selects a random enemy template and creates an Enemy instance.

        Returns:
            Optional[Enemy]: An Enemy instance, or None if no templates are available
                             or an error occurs during instantiation.
        """
        if not self.enemy_templates:
            print("Error: No enemy templates available to create an enemy.")
            return None

        try:
            template = random.choice(self.enemy_templates)  # nosec B311 - Non-cryptographic use for game mechanics
            return Enemy(
                name=template["name"],
                max_hp=template["hp"],
                attack_stat=template["attack_stat"],
                loot_gold_min=template["loot_gold_min"],
                loot_gold_max=template["loot_gold_max"]
            )
        except KeyError as e:
            print(f"Error: Enemy template is missing a required key: {e}. Template: {template}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while creating an enemy: {e}")
            return None

