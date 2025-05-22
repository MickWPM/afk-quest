import math

class Character:
    """
    Represents a player character in the game.
    Manages attributes, experience, health, and equipment.
    """
    def __init__(self, name: str, level: int = 1, current_experience: int = 0,
                 gold: int = 0, equipment: dict = None, current_hp: int = -1):
        self.name: str = name
        self.level: int = level
        self.current_experience: int = current_experience
        self.gold: int = gold
        self.equipment: dict = equipment if equipment is not None else {
            "weapon": None, "armour": None, "item": None
        }
        self.is_dead: bool = False

        # Calculated stats
        self.experience_to_next_level: int = 0
        self.max_hp: int = 0
        self._update_stats_for_level() # Initial calculation

        if current_hp == -1:
            self.current_hp: int = self.max_hp
        else:
            self.current_hp: int = min(current_hp, self.max_hp) # Ensure current_hp doesn't exceed max_hp from load

        if self.current_hp <= 0: # Check if loaded character should be dead
            self.current_hp = 0
            self.is_dead = True


    def _update_stats_for_level(self):
        """
        Private method to recalculate max_hp and experience_to_next_level
        based on the current level.
        """
        self.max_hp = self.level * 15
        self.experience_to_next_level = self.level * 10

    def gain_experience(self, amount: int):
        """
        Adds experience to the character. Handles leveling up, including
        multiple levels from one gain, and ensures current_experience
        correctly reflects points into the new level.
        """
        if amount <= 0:
            return

        self.current_experience += amount
        leveled_up = False

        while self.current_experience >= self.experience_to_next_level:
            self.current_experience -= self.experience_to_next_level
            self.level += 1
            self._update_stats_for_level()
            # When leveling up, HP increases. Restore to full HP or add the difference.
            # For simplicity, let's restore to full HP on level up for now.
            self.current_hp = self.max_hp
            leveled_up = True
            print(f"Ding! {self.name} reached Level {self.level}!")

        if leveled_up and self.is_dead: # If leveled up while dead (e.g. posthumous XP), still dead but new stats
             pass # Or revive if game design desires, for now, stays dead.
        elif leveled_up: # Ensure not dead if was alive and leveled up
            self.is_dead = False


    def take_damage(self, amount: int):
        """
        Reduces current_hp by the given amount.
        Sets is_dead to True if current_hp drops to 0 or below.
        Ensures current_hp doesn't go below 0.
        """
        if amount <= 0:
            return

        self.current_hp -= amount
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
            print(f"{self.name} has taken {amount} damage and has fallen!")
        else:
            print(f"{self.name} takes {amount} damage. {self.current_hp}/{self.max_hp} HP remaining.")

    def heal(self, amount: int):
        """
        Increases current_hp by the given amount.
        Ensures current_hp doesn't exceed max_hp.
        If character was dead and current_hp > 0 after healing, sets is_dead to False.
        """
        if amount <= 0:
            return

        if self.is_dead and self.current_hp <= 0 and amount > 0 : # Only print revived if actually healing from 0
             print(f"{self.name} is being revived!")

        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

        if self.current_hp > 0 and self.is_dead:
            self.is_dead = False
            # print(f"{self.name} has been revived!") # Covered by initial print

        print(f"{self.name} heals for {amount}. {self.current_hp}/{self.max_hp} HP.")


    def add_gold(self, amount: int):
        """Increases gold count."""
        if amount > 0:
            self.gold += amount
            print(f"{self.name} found {amount} gold. Total: {self.gold} gold.")
        elif amount < 0:
            # Potentially allow losing gold if needed in future
            print("Cannot add a negative amount of gold through this method.")


    def get_summary(self) -> str:
        """
        Returns a formatted string detailing Name, Level, HP (current/max),
        EXP (current/to next), Gold, and Equipment.
        """
        status = "Alive"
        if self.is_dead:
            status = "Dead"
        summary = (
            f"--- Character Summary ---\n"
            f"Name: {self.name}\n"
            f"Level: {self.level} ({status})\n"
            f"HP: {self.current_hp}/{self.max_hp}\n"
            f"EXP: {self.current_experience}/{self.experience_to_next_level}\n"
            f"Gold: {self.gold}\n"
            f"Equipment:\n"
            f"  Weapon: {self.equipment.get('weapon', 'None')}\n"
            f"  Armour: {self.equipment.get('armour', 'None')}\n"
            f"  Item: {self.equipment.get('item', 'None')}\n"
            f"-------------------------"
        )
        return summary

    def to_dict(self) -> dict:
        """Serializes character data to a dictionary for saving."""
        return {
            "name": self.name,
            "level": self.level,
            "current_experience": self.current_experience,
            "current_hp": self.current_hp,
            "gold": self.gold,
            "equipment": self.equipment,
            # is_dead is implicitly handled by current_hp on load
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """Deserializes character data from a dictionary to create a Character instance."""
        return cls(
            name=data["name"],
            level=data["level"],
            current_experience=data["current_experience"],
            current_hp=data["current_hp"],
            gold=data["gold"],
            equipment=data["equipment"]
        )