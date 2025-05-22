import pytest
from src.character import Character # Assuming src is in PYTHONPATH or using a project runner

class TestCharacter:
    def test_creation_default_values(self):
        char = Character(name="TestDefault")
        assert char.name == "TestDefault"
        assert char.level == 1
        assert char.current_experience == 0
        assert char.gold == 0
        assert char.equipment == {"weapon": None, "armour": None, "item": None}
        assert char.max_hp == 1 * 15
        assert char.experience_to_next_level == 1 * 10
        assert char.current_hp == char.max_hp
        assert not char.is_dead

    def test_creation_custom_values(self):
        custom_equip = {"weapon": "Stick", "armour": "Rags", "item": "Rock"}
        char = Character(name="TestCustom", level=3, current_experience=5, gold=100,
                         equipment=custom_equip, current_hp=20)
        assert char.name == "TestCustom"
        assert char.level == 3
        assert char.current_experience == 5
        assert char.gold == 100
        assert char.equipment == custom_equip
        assert char.max_hp == 3 * 15
        assert char.experience_to_next_level == 3 * 10
        assert char.current_hp == 20 # Max HP for L3 is 45, so 20 is valid
        assert not char.is_dead

    def test_creation_hp_capped_at_max(self):
        char = Character(name="HighHP", level=2, current_hp=100) # Max HP for L2 is 30
        assert char.max_hp == 30
        assert char.current_hp == 30

    def test_creation_dead_if_hp_zero_or_less(self):
        char_zero_hp = Character(name="ZeroHP", level=1, current_hp=0)
        assert char_zero_hp.current_hp == 0
        assert char_zero_hp.is_dead

        char_neg_hp = Character(name="NegHP", level=1, current_hp=-10)
        assert char_neg_hp.current_hp == 0 # Should be floored to 0
        assert char_neg_hp.is_dead


    def test_gain_experience_no_level_up(self):
        char = Character(name="Learner") # EXP to next: 10
        char.gain_experience(5)
        assert char.current_experience == 5
        assert char.level == 1

    def test_gain_experience_single_level_up(self):
        char = Character(name="LevelUpper", level=1) # EXP to next L2: 10
        char.gain_experience(12) # Should level to 2, have 2 EXP into L2
        assert char.level == 2
        assert char.current_experience == 2
        assert char.experience_to_next_level == 2 * 10 # 20 for L3
        assert char.max_hp == 2 * 15 # 30
        assert char.current_hp == char.max_hp # Healed on level up
        assert not char.is_dead

    def test_gain_experience_multiple_level_ups(self):
        char = Character(name="FastLearner", level=1) # L1->L2: 10xp, L2->L3: 20xp. Total 30xp for L3
        char.gain_experience(35) # Should reach L3, have 5 EXP into L3
        assert char.level == 3
        assert char.current_experience == 5
        assert char.experience_to_next_level == 3 * 10 # 30 for L4
        assert char.max_hp == 3 * 15 # 45
        assert char.current_hp == char.max_hp # Healed on level up

    def test_gain_experience_exact_to_level_up(self):
        char = Character(name="ExactLearner")
        char.gain_experience(10) # Exactly levels to 2
        assert char.level == 2
        assert char.current_experience == 0
        assert char.experience_to_next_level == 20

    def test_gain_zero_or_negative_experience(self):
        char = Character(name="NoXP")
        initial_exp = char.current_experience
        char.gain_experience(0)
        assert char.current_experience == initial_exp
        char.gain_experience(-5)
        assert char.current_experience == initial_exp


    def test_take_damage_updates_hp(self):
        char = Character(name="Hurt")
        initial_hp = char.current_hp
        char.take_damage(5)
        assert char.current_hp == initial_hp - 5
        assert not char.is_dead

    def test_take_damage_sets_is_dead_flag(self):
        char = Character(name="Doomed", level=1) # Max HP 15
        char.take_damage(15)
        assert char.current_hp == 0
        assert char.is_dead

    def test_take_damage_hp_does_not_go_below_zero(self):
        char = Character(name="Overkill", level=1) # Max HP 15
        char.take_damage(100)
        assert char.current_hp == 0
        assert char.is_dead

    def test_take_zero_or_negative_damage(self):
        char = Character(name="Tough")
        initial_hp = char.current_hp
        char.take_damage(0)
        assert char.current_hp == initial_hp
        char.take_damage(-5)
        assert char.current_hp == initial_hp


    def test_heal_updates_hp(self):
        char = Character(name="Mending", level=1) # Max HP 15
        char.take_damage(10) # HP is 5
        char.heal(5)
        assert char.current_hp == 10
        assert not char.is_dead

    def test_heal_does_not_exceed_max_hp(self):
        char = Character(name="FullHeal", level=1) # Max HP 15
        char.take_damage(1) # HP is 14
        char.heal(100)
        assert char.current_hp == char.max_hp
        assert not char.is_dead

    def test_heal_revives_dead_character(self):
        char = Character(name="Revival", level=1) # Max HP 15
        char.take_damage(15) # Dies
        assert char.is_dead
        char.heal(5)
        assert char.current_hp == 5
        assert not char.is_dead

    def test_heal_dead_character_to_full(self):
        char = Character(name="FullRevive", level=1)
        char.take_damage(char.max_hp)
        assert char.is_dead
        char.heal(char.max_hp + 5) # Heal more than max
        assert char.current_hp == char.max_hp
        assert not char.is_dead

    def test_heal_zero_or_negative_amount(self):
        char = Character(name="NoHeal")
        char.take_damage(5)
        initial_hp = char.current_hp
        char.heal(0)
        assert char.current_hp == initial_hp
        char.heal(-5)
        assert char.current_hp == initial_hp

    def test_add_gold(self):
        char = Character(name="Rich")
        char.add_gold(50)
        assert char.gold == 50
        char.add_gold(25)
        assert char.gold == 75

    def test_add_negative_gold(self, capsys):
        char = Character(name="PoorAttempt")
        initial_gold = char.gold
        char.add_gold(-10)
        assert char.gold == initial_gold
        captured = capsys.readouterr()
        assert "Cannot add a negative amount of gold" in captured.out


    def test_get_summary_contains_essential_info(self):
        char = Character(name="SummaryChar", level=2, current_experience=5, gold=50)
        char.equipment["weapon"] = "Rusty Sword"
        char.take_damage(10) # HP: 30 -> 20 for L2
        summary = char.get_summary()
        assert "SummaryChar" in summary
        assert "Level: 2" in summary
        assert f"HP: {char.current_hp}/{char.max_hp}" in summary # HP: 20/30
        assert f"EXP: {char.current_experience}/{char.experience_to_next_level}" in summary # EXP: 5/20
        assert "Gold: 50" in summary
        assert "Weapon: Rusty Sword" in summary
        assert "Armour: None" in summary
        assert "Alive" in summary

    def test_get_summary_dead_status(self):
        char = Character(name="DeadSummary")
        char.take_damage(char.max_hp * 2) # Ensure dead
        summary = char.get_summary()
        assert "Dead" in summary

    def test_to_dict_serialization(self):
        equip = {"weapon": "Dagger", "armour": None, "item": "Potion"}
        char = Character(name="Serializer", level=5, current_experience=12,
                         current_hp=60, gold=200, equipment=equip)
        char_dict = char.to_dict()
        expected_dict = {
            "name": "Serializer",
            "level": 5,
            "current_experience": 12,
            "current_hp": 60, # Max HP for L5 is 75.
            "gold": 200,
            "equipment": equip
        }
        assert char_dict == expected_dict

    def test_from_dict_deserialization(self):
        data = {
            "name": "Deserializer",
            "level": 3,
            "current_experience": 3,
            "current_hp": 30, # Max HP for L3 is 45.
            "gold": 150,
            "equipment": {"weapon": None, "armour": "Leather", "item": None}
        }
        char = Character.from_dict(data)
        assert char.name == "Deserializer"
        assert char.level == 3
        assert char.current_experience == 3
        assert char.max_hp == 3 * 15
        assert char.current_hp == 30
        assert char.experience_to_next_level == 3 * 10
        assert char.gold == 150
        assert char.equipment == {"weapon": None, "armour": "Leather", "item": None}
        assert not char.is_dead

    def test_from_dict_deserialization_dead_character(self):
        data = {
            "name": "DeadLoad",
            "level": 2,
            "current_experience": 5,
            "current_hp": 0,
            "gold": 10,
            "equipment": {"weapon": None, "armour": None, "item": None}
        }
        char = Character.from_dict(data)
        assert char.name == "DeadLoad"
        assert char.level == 2
        assert char.current_hp == 0
        assert char.is_dead