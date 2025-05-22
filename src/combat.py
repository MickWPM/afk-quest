import random
import time # For slight pauses to make combat readable
from .character import Character # Relative import
from .enemy import Enemy # Relative import

def start_combat(player: Character, enemy: Enemy):
    """
    Manages a combat encounter between the player and an enemy.

    Args:
        player (Character): The player character.
        enemy (Enemy): The enemy instance.

    Returns:
        str: A string indicating the outcome ("player_won", "player_lost", "player_fled" - though flee not in P2).
    """
    print("\n--- COMBAT START ---")
    print(f"{player.name} (HP: {player.current_hp}/{player.max_hp}) vs. {enemy.name} (HP: {enemy.current_hp}/{enemy.max_hp})")
    print("--------------------")
    time.sleep(1)

    round_num = 1
    while not player.is_dead and not enemy.is_dead:
        print(f"\n--- Round {round_num} ---")

        # Player's turn
        player_attack_power = player.get_attack_power()
        # Damage is randomized between 0 and attack_power (inclusive of 0 for a "miss" or ineffective hit)
        player_damage = random.randint(0, player_attack_power)

        if player_damage > 0:
            print(f"{player.name} attacks {enemy.name} for {player_damage} damage!")
            enemy.take_damage(player_damage)
        else:
            print(f"{player.name} attacks {enemy.name} but misses or the blow is ineffective!")

        print(f"{enemy.name} HP: {enemy.current_hp}/{enemy.max_hp}")
        time.sleep(1)

        if enemy.is_dead:
            print(f"\n{enemy.name} has been defeated!")
            loot_gold = enemy.get_loot_gold()
            if loot_gold > 0:
                print(f"{player.name} loots {loot_gold} gold from {enemy.name}.")
                player.add_gold(loot_gold) # This will print its own message
            # XP gain could happen here or be returned for game.py to handle
            # For now, let's say 5 XP per enemy level (or fixed XP)
            xp_gained = enemy.max_hp // 2 # Example: XP based on enemy toughness
            print(f"{player.name} gains {xp_gained} experience points!")
            player.gain_experience(xp_gained)
            time.sleep(3)
            return "player_won"

        # Enemy's turn
        enemy_attack_power = enemy.attack_stat
        enemy_damage = random.randint(0, enemy_attack_power)

        if enemy_damage > 0:
            print(f"{enemy.name} retaliates, attacking {player.name} for {enemy_damage} damage!")
            damage_log = player.take_damage(enemy_damage) # take_damage now returns a log
            print(damage_log)
        else:
            print(f"{enemy.name} attacks {player.name} but misses or the attack is clumsy!")

        print(f"{player.name} HP: {player.current_hp}/{player.max_hp}")
        time.sleep(1)

        if player.is_dead:
            print(f"\nAlas, {player.name} has been defeated by {enemy.name}...")
            time.sleep(3)
            return "player_lost"

        round_num += 1
        input("Press Enter to continue to the next round...")
        print("--------------------")

    # Should not be reached if logic is correct, but as a fallback:
    if player.is_dead: return "player_lost"
    if enemy.is_dead: return "player_won" # Should have been caught earlier
    return "stalemate" # Unlikely with this combat model
