import random

class Enemy:
    """
    Represents an enemy in the game.
    """
    def __init__(self, name: str, max_hp: int, attack_stat: int, loot_gold_min: int, loot_gold_max: int):
        """
        Initializes an Enemy instance.

        Args:
            name (str): The name of the enemy.
            max_hp (int): The maximum health points of the enemy.
            attack_stat (int): The base attack power of the enemy (max damage).
            loot_gold_min (int): The minimum amount of gold this enemy can drop.
            loot_gold_max (int): The maximum amount of gold this enemy can drop.
        """
        self.name: str = name
        self.max_hp: int = max_hp
        self.current_hp: int = max_hp
        self.attack_stat: int = attack_stat # Max damage enemy can do
        self.loot_gold_min: int = loot_gold_min
        self.loot_gold_max: int = loot_gold_max
        self.is_dead: bool = False

    def take_damage(self, amount: int):
        """
        Applies damage to the enemy.

        Args:
            amount (int): The amount of damage to apply.
        """
        if amount <= 0:
            return

        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
            # print(f"{self.name} has taken {amount} damage and has been defeated!") # Combat log will handle
        # else:
            # print(f"{self.name} takes {amount} damage. {self.current_hp}/{self.max_hp} HP remaining.")

    def get_loot_gold(self) -> int:
        """
        Determines the amount of gold dropped by this enemy.

        Returns:
            int: The amount of gold.
        """
        if self.loot_gold_max < self.loot_gold_min: # Should not happen with validation
            return self.loot_gold_min
        return random.randint(self.loot_gold_min, self.loot_gold_max)

    def get_summary(self) -> str:
        """
        Returns a string summary of the enemy's status.
        """
        status = "Defeated" if self.is_dead else "Ready"
        return (f"{self.name} | HP: {self.current_hp}/{self.max_hp} | Status: {status}")

