from .character import Character
from . import file_manager
from .data_loader import DataLoader # New import
from .enemy_manager import EnemyManager # New import
from . import combat # New import

# Global instances (or pass them around if preferred for larger apps)
# Initialize DataLoader - assumes 'data' folder is in the root project directory
# where the game is run from (e.g., python -m src.game from afk_quest/)
data_loader = DataLoader(data_folder_path="data")
enemy_definitions = data_loader.load_enemy_definitions()
enemy_manager = EnemyManager(enemy_templates=enemy_definitions)


def prompt_create_new_character() -> Character:
    """Asks user for name, creates and returns a new Character."""
    while True:
        name = input("Enter your character's name: ").strip()
        if name:
            return Character(name=name)
        print("Name cannot be empty. Please try again.")

def display_main_menu(character_exists: bool):
    """Shows options (Continue, New Game, Quit)."""
    print("\n--- Main Menu ---")
    if character_exists:
        print("1. Continue Game")
    print("2. Start New Game")
    print("3. Quit")
    print("-----------------")
    while True:
        choice = input("Enter your choice: ")
        if character_exists and choice == "1":
            return "continue"
        if choice == "2":
            return "new"
        if choice == "3":
            return "quit"
        print("Invalid choice. Please try again.")

def display_action_menu(character_alive: bool): # Added character_alive
    """Shows game actions."""
    print("\n--- Actions ---")
    if character_alive: # Only show these if alive
        print("1. Add Experience (Debug)")
        print("2. Take Damage (Debug)")
        print("3. Heal (Debug)")
        print("4. Add Gold (Debug)")
        print("5. Look for a Fight") # New action
    print("S. View Character Summary") # Changed to S for summary
    print("Q. Save and Quit to Main Menu") # Changed to Q
    print("---------------")
    while True:
        choice = input("Enter your action: ").upper() # Convert to uppercase
        if character_alive:
            if choice in ["1", "2", "3", "4", "5"]:
                return choice
        if choice in ["S", "Q"]:
            return choice
        print("Invalid action. Please try again.")

def get_int_input(prompt: str) -> int:
    """Safely gets an integer input from the user."""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def run():
    """Main game loop."""
    current_character: Character | None = None
    print("Welcome to AFK Quest!")
    if not enemy_definitions: # Check if enemy definitions loaded
        print("Critical Error: Could not load enemy definitions. Combat will not be available.")
        # Potentially exit or disable combat features

    while True: # Outer loop for Main Menu
        existing_char_data = file_manager.load_character()
        main_menu_choice = display_main_menu(character_exists=(existing_char_data is not None))

        if main_menu_choice == "continue":
            if existing_char_data:
                current_character = existing_char_data
                print(f"\nWelcome back, {current_character.name}!")
            else:
                print("No character data found. Starting new game.")
                current_character = prompt_create_new_character()
        elif main_menu_choice == "new":
            current_character = prompt_create_new_character()
            print(f"\nWelcome, {current_character.name}!")
        elif main_menu_choice == "quit":
            print("Thanks for playing AFK Quest!")
            break

        if current_character:
            print(current_character.get_summary())
            # Inner loop for actions
            while True:
                if current_character.is_dead:
                    print(f"\nAlas, {current_character.name} has perished.")
                    print("You can view your character summary or return to the main menu.")
                
                action_choice = display_action_menu(character_alive=not current_character.is_dead)

                if action_choice == "1" and not current_character.is_dead: # Add EXP
                    amount = get_int_input("Enter EXP to add: ")
                    current_character.gain_experience(amount)
                elif action_choice == "2" and not current_character.is_dead: # Take Damage
                    amount = get_int_input("Enter damage to take: ")
                    log = current_character.take_damage(amount)
                    print(log)
                elif action_choice == "3" and not current_character.is_dead: # Heal
                    amount = get_int_input("Enter amount to heal: ")
                    log = current_character.heal(amount)
                    print(log)
                elif action_choice == "4" and not current_character.is_dead: # Add Gold
                    amount = get_int_input("Enter gold to add: ")
                    current_character.add_gold(amount)
                elif action_choice == "5" and not current_character.is_dead: # Look for a Fight
                    if not enemy_manager or not enemy_manager.enemy_templates:
                        print("No enemies available to fight at the moment. Check enemy definitions.")
                    else:
                        enemy_to_fight = enemy_manager.get_random_enemy()
                        if enemy_to_fight:
                            combat_result = combat.start_combat(current_character, enemy_to_fight)
                            print(f"\n--- Combat Over ---")
                            if combat_result == "player_won":
                                print("You were victorious!")
                            elif combat_result == "player_lost":
                                print("You have been defeated.")
                                # Character is already marked as dead by take_damage
                            # Player summary will be printed next, or death message if applicable
                        else:
                            print("Could not find an enemy to fight. Perhaps they are all hiding?")
                elif action_choice == "S": # Summary
                    pass # Summary is printed after each action anyway if alive
                elif action_choice == "Q": # Save and Quit to Main Menu
                    file_manager.save_character(current_character)
                    current_character = None
                    break

                if current_character: # Re-check in case of future modifications
                    print(current_character.get_summary())
                    if current_character.is_dead:
                        # Handled at the start of the action loop
                        continue # Go back to displaying limited menu for dead char
                else: # Character quit to main menu
                    break
        else:
            # This case should ideally not be reached if logic is sound
            print("Error: No character loaded. Returning to main menu.")

if __name__ == "__main__":
    print("Starting AFK Quest...")
    run()
