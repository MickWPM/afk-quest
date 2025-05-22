from .character import Character # Relative import
from . import file_manager # Relative import

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

def display_action_menu():
    """Shows game actions (Add EXP, Damage, Heal, Add Gold, Character Summary, Quit to Main Menu)."""
    print("\n--- Actions ---")
    print("1. Add Experience")
    print("2. Take Damage")
    print("3. Heal")
    print("4. Add Gold")
    print("5. View Character Summary")
    print("6. Save and Quit to Main Menu")
    print("---------------")
    while True:
        choice = input("Enter your action: ")
        if choice in ["1", "2", "3", "4", "5", "6"]:
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

    while True: # Outer loop for Main Menu
        existing_char_data = file_manager.load_character()
        main_menu_choice = display_main_menu(character_exists=(existing_char_data is not None))

        if main_menu_choice == "continue":
            if existing_char_data:
                current_character = existing_char_data
                print(f"\nWelcome back, {current_character.name}!")
            else: # Should not happen if menu logic is correct
                print("No character data found. Starting new game.")
                current_character = prompt_create_new_character()
        elif main_menu_choice == "new":
            current_character = prompt_create_new_character()
            print(f"\nWelcome, {current_character.name}!")
        elif main_menu_choice == "quit":
            print("Thanks for playing AFK Quest!")
            break # Exit outer loop (and program)

        if current_character:
            print(current_character.get_summary())
            # Inner loop for actions
            while True:
                action_choice = display_action_menu()

                if action_choice == "1": # Add EXP
                    amount = get_int_input("Enter EXP to add: ")
                    current_character.gain_experience(amount)
                elif action_choice == "2": # Take Damage
                    amount = get_int_input("Enter damage to take: ")
                    current_character.take_damage(amount)
                elif action_choice == "3": # Heal
                    amount = get_int_input("Enter amount to heal: ")
                    current_character.heal(amount)
                elif action_choice == "4": # Add Gold
                    amount = get_int_input("Enter gold to add: ")
                    current_character.add_gold(amount)
                elif action_choice == "5": # Summary
                    pass # Summary is printed after each action anyway
                elif action_choice == "6": # Save and Quit to Main Menu
                    file_manager.save_character(current_character)
                    current_character = None # Clear current character for main menu logic
                    break # Exit inner loop, back to main menu

                if current_character: # Re-check in case of future modifications
                    print(current_character.get_summary())
                    if current_character.is_dead:
                        print(f"\nAlas, {current_character.name} has perished. Game over for this character.")
                        print("You will be returned to the main menu. The character file remains.")
                        # No automatic save on death, player can choose to save if they quit from menu
                        current_character = None # Clear current character
                        break # Exit inner loop, back to main menu
        else:
            # This case should ideally not be reached if logic is sound
            print("Error: No character loaded. Returning to main menu.")

if __name__ == "__main__":
    # This allows running the game directly from game.py for testing,
    # but you'd typically have a main entry point script.
    # For now, to run, you would navigate to afk_quest/ directory and run: python -m src.game
    print("Starting AFK Quest...")
    run()