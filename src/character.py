import math

class Character:
    """
    Represents a player character in the game.
    Manages attributes, experience, health, and equipment.
    """
    def __init__(self, name: str, level: int = 1, current_experience: int = 0,
                 gold: int = 0, equipment: dict = None, current_hp: int = -1,
                 base_attack_stat: int = 1): # Added base_attack_stat
        self.name: str = name
        self.level: int = level
        self.current_experience: int = current_experience
        self.gold: int = gold
        self.equipment: dict = equipment if equipment is not None else {
            "weapon": None, "armour": None, "item": None
        }
        self.is_dead: bool = False
        self.base_attack_stat: int = base_attack_stat # Player's unarmed attack

        # Calculated stats
        self.experience_to_next_level: int = 0
        self.max_hp: int = 0
        self._update_stats_for_level() # Initial calculation

        if current_hp == -1:
            self.current_hp: int = self.max_hp
        else:
            self.current_hp: int = min(current_hp, self.max_hp)

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True


    def _update_stats_for_level(self):
        """
        Private method to recalculate max_hp and experience_to_next_level
        based on the current level.
        """
        self.max_hp = self.level * 15
        self.experience_to_next_level = self.level * 10
        # Potentially increase base_attack_stat with level in future
        # self.base_attack_stat = 1 + math.floor(self.level / 5) # Example

    def gain_experience(self, amount: int):
        """
        Adds experience to the character. Handles leveling up.
        """
        if amount <= 0 or self.is_dead: # Cannot gain XP if dead (or can, depends on game rules)
            return

        self.current_experience += amount
        leveled_up_this_gain = False

        while self.current_experience >= self.experience_to_next_level:
            self.current_experience -= self.experience_to_next_level
            self.level += 1
            old_max_hp = self.max_hp
            self._update_stats_for_level()
            hp_increase = self.max_hp - old_max_hp
            self.current_hp = min(self.max_hp, self.current_hp + hp_increase) # Add HP increase, don't just set to full
            leveled_up_this_gain = True
            print(f"Ding! {self.name} reached Level {self.level}!")

        if leveled_up_this_gain: # If leveled up, ensure not dead if was alive
            if self.current_hp > 0:
                 self.is_dead = False

    def get_attack_power(self) -> int:
        """
        Calculates the character's current attack power.
        For Phase 2, this is just the base_attack_stat as weapons are not implemented.
        Future: Add weapon damage.
        """
        # Example for future:
        # weapon_damage = self.equipment.get("weapon").damage if self.equipment.get("weapon") else 0
        # return self.base_attack_stat + weapon_damage
        return self.base_attack_stat

    def get_damage_reduction(self) -> int:
        """
        Calculates the character's current damage reduction from armour.
        For Phase 2, this is 0 as armour is not implemented.
        Future: Add armour value.
        """
        # Example for future:
        # armour_value = self.equipment.get("armour").reduction if self.equipment.get("armour") else 0
        # return armour_value
        return 0

    def take_damage(self, amount: int):
        """
        Reduces current_hp by the given amount, considering damage reduction.
        Sets is_dead to True if current_hp drops to 0 or below.
        """
        if amount <= 0:
            return

        damage_reduction = self.get_damage_reduction()
        actual_damage = max(0, amount - damage_reduction) # Damage cannot be negative

        self.current_hp -= actual_damage
        log_message = f"{self.name} takes {actual_damage} damage"
        if damage_reduction > 0:
            log_message += f" ({amount} incoming, {damage_reduction} reduced by armour)."
        else:
            log_message += "."

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_dead = True
            log_message += f" {self.name} has fallen!"
        else:
            log_message += f" {self.current_hp}/{self.max_hp} HP remaining."
        # print(log_message) # Combat log will handle this. Return it instead?
        return log_message # Return the log message for the combat system to print


    def heal(self, amount: int):
        """
        Increases current_hp by the given amount.
        """
        if amount <= 0:
            return "" # Return empty string if no healing done

        heal_message = ""
        if self.is_dead and self.current_hp <= 0 and amount > 0 :
             heal_message += f"{self.name} is being revived! "

        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

        if self.current_hp > 0 and self.is_dead:
            self.is_dead = False
            # heal_message += f"{self.name} has been revived! " # Covered

        heal_message += f"{self.name} heals for {amount}. {self.current_hp}/{self.max_hp} HP."
        # print(heal_message)
        return heal_message


    def add_gold(self, amount: int):
        """Increases gold count."""
        if amount > 0:
            self.gold += amount
            print(f"{self.name} found {amount} gold. Total: {self.gold} gold.")
        elif amount < 0:
            print("Cannot add a negative amount of gold through this method.")


    def get_summary(self) -> str:
        """
        Returns a formatted string detailing Name, Level, HP (current/max),
        EXP (current/to next), Gold, and Equipment.
        """
        status = "Dead" if self.is_dead else "Alive"
        summary = (
            f"--- Character Summary ---\n"
            f"Name: {self.name} (Level: {self.level} - {status})\n"
            f"HP: {self.current_hp}/{self.max_hp}\n"
            f"EXP: {self.current_experience}/{self.experience_to_next_level}\n"
            f"Attack Power: {self.get_attack_power()} | Damage Reduction: {self.get_damage_reduction()}\n"
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
            "base_attack_stat": self.base_attack_stat
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """Deserializes character data from a dictionary to create a Character instance."""
        return cls(
            name=data["name"],
            level=data.get("level", 1), # Default level if not in old save
            current_experience=data.get("current_experience", 0),
            current_hp=data.get("current_hp", -1), # Will default to max_hp if -1
            gold=data.get("gold", 0),
            equipment=data.get("equipment", {"weapon": None, "armour": None, "item": None}),
            base_attack_stat=data.get("base_attack_stat", 1) # Default for old saves
        )
