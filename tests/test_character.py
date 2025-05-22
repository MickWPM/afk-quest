import pytest
from src.character import Character # Assuming src is in PYTHONPATH or using a project runner

class TestCharacter:
    # ... (Other existing tests) ...

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
        assert char.base_attack_stat == 1 # Default

    def test_creation_custom_values(self):
        custom_equip = {"weapon": "Stick", "armour": "Rags", "item": "Rock"}
        char = Character(name="TestCustom", level=3, current_experience=5, gold=100,
                         equipment=custom_equip, current_hp=20, base_attack_stat=2) # Added base_attack_stat
        assert char.name == "TestCustom"
        assert char.level == 3
        assert char.current_experience == 5
        assert char.gold == 100
        assert char.equipment == custom_equip
        assert char.max_hp == 3 * 15
        assert char.experience_to_next_level == 3 * 10
        assert char.current_hp == 20
        assert not char.is_dead
        assert char.base_attack_stat == 2

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
        char.take_damage(1) # HP 14/15
        initial_hp_before_level = char.current_hp
        hp_increase_expected = (2*15) - (1*15)

        char.gain_experience(12) # Should level to 2, have 2 EXP into L2
        assert char.level == 2
        assert char.current_experience == 2
        assert char.experience_to_next_level == 2 * 10 # 20 for L3
        assert char.max_hp == 2 * 15 # 30
        assert char.current_hp == min(char.max_hp, initial_hp_before_level + hp_increase_expected)
        assert not char.is_dead

    def test_gain_experience_multiple_level_ups(self):
        char = Character(name="FastLearner", level=1) # L1->L2: 10xp, L2->L3: 20xp. Total 30xp for L3
        char.take_damage(1) # HP 14/15
        initial_hp_before_levels = char.current_hp
        expected_max_hp_at_l3 = 3 * 15
        original_max_hp_at_l1 = 1 * 15
        total_hp_increase_expected = expected_max_hp_at_l3 - original_max_hp_at_l1

        char.gain_experience(35) # Should reach L3, have 5 EXP into L3
        assert char.level == 3
        assert char.current_experience == 5
        assert char.experience_to_next_level == 3 * 10 # 30 for L4
        assert char.max_hp == expected_max_hp_at_l3
        assert char.current_hp == min(char.max_hp, initial_hp_before_levels + total_hp_increase_expected)

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
        char = Character(name="SummaryChar", level=2, current_experience=5, gold=50, base_attack_stat=2)
        char.equipment["weapon"] = "Rusty Sword"
        char.take_damage(10) # HP: 30 -> 20 for L2
        summary = char.get_summary()
        assert "SummaryChar" in summary
        assert "Level: 2" in summary
        assert f"HP: {char.current_hp}/{char.max_hp}" in summary
        assert f"EXP: {char.current_experience}/{char.experience_to_next_level}" in summary
        assert "Attack Power: 2" in summary # Check base_attack_stat
        assert "Damage Reduction: 0" in summary
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
        # Character created here will have base_attack_stat = 1 (default)
        char = Character(name="Serializer", level=5, current_experience=12,
                         current_hp=60, gold=200, equipment=equip)
        char_dict = char.to_dict()
        expected_dict = {
            "name": "Serializer",
            "level": 5,
            "current_experience": 12,
            "current_hp": 60,
            "gold": 200,
            "equipment": equip,
            "base_attack_stat": 1 # Added: char will have default base_attack_stat of 1
        }
        assert char_dict == expected_dict

    def test_from_dict_deserialization(self):
        data = {
            "name": "Deserializer",
            "level": 3,
            "current_experience": 3,
            "current_hp": 30,
            "gold": 150,
            "equipment": {"weapon": None, "armour": "Leather", "item": None},
            "base_attack_stat": 2 # Explicitly providing it here
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
        assert char.base_attack_stat == 2 # Check it's loaded
        assert char.get_attack_power() == 2


    def test_from_dict_deserialization_dead_character(self):
        data = {
            "name": "DeadLoad",
            "level": 2,
            "current_experience": 5,
            "current_hp": 0,
            "gold": 10,
            "equipment": {"weapon": None, "armour": None, "item": None},
            "base_attack_stat": 1
        }
        char = Character.from_dict(data)
        assert char.name == "DeadLoad"
        assert char.level == 2
        assert char.current_hp == 0
        assert char.is_dead
        assert char.base_attack_stat == 1

    # New tests for combat-related methods from Phase 2
    def test_creation_with_base_attack(self):
        char = Character(name="Attacker", base_attack_stat=2)
        assert char.base_attack_stat == 2
        assert char.get_attack_power() == 2

    def test_default_base_attack(self): # Already somewhat covered by test_creation_default_values
        char = Character(name="DefaultAttacker")
        assert char.base_attack_stat == 1
        assert char.get_attack_power() == 1

    def test_get_damage_reduction_default(self):
        char = Character(name="Defender")
        assert char.get_damage_reduction() == 0

    def test_take_damage_with_reduction(self):
        char = Character(name="Tank", level=1) # Max HP 15
        log = char.take_damage(10)
        assert char.current_hp == 5
        assert "takes 10 damage." in log
        assert "reduced by armour" not in log # Since reduction is 0

    def test_take_damage_actual_damage_non_negative(self):
        char = Character(name="ToughGuy", level=1)
        log = char.take_damage(5)
        assert char.current_hp == char.max_hp - 5

    def test_heal_returns_log_message(self):
        char = Character(name="HealedOne", level=1)
        char.take_damage(10) # HP 5/15
        log = char.heal(5)
        assert char.current_hp == 10
        assert "heals for 5" in log
        assert "10/15 HP" in log

    def test_heal_dead_character_returns_revive_log(self):
        char = Character(name="RevivedOne", level=1)
        char.take_damage(char.max_hp) # Dies
        log = char.heal(5)
        assert "is being revived!" in log
        assert "heals for 5" in log
        assert not char.is_dead

    def test_gain_experience_hp_increase_on_level_up(self):
        char = Character(name="LevelUpperHP", level=1) # Max HP 15, EXP to L2: 10
        char.take_damage(5) # HP is 10/15
        initial_hp = char.current_hp
        hp_increase_on_level = (2*15) - (1*15) # MaxHP L2 - MaxHP L1
        char.gain_experience(10) # Levels to 2
        assert char.level == 2
        assert char.max_hp == 30
        assert char.current_hp == min(char.max_hp, initial_hp + hp_increase_on_level)
        assert not char.is_dead

    def test_to_dict_includes_base_attack_stat(self): # This is a duplicate of the one being fixed
        char = Character(name="DictChar", base_attack_stat=3)
        char_dict = char.to_dict()
        assert "base_attack_stat" in char_dict
        assert char_dict["base_attack_stat"] == 3

    def test_from_dict_loads_base_attack_stat(self): # This is a duplicate
        data = {
            "name": "LoadedAttacker", "level": 1, "current_experience": 0,
            "current_hp": 15, "gold": 0, "equipment": {}, "base_attack_stat": 2
        }
        char = Character.from_dict(data)
        assert char.base_attack_stat == 2
        assert char.get_attack_power() == 2

    def test_from_dict_defaults_base_attack_stat_for_old_saves(self):
        old_data = {
            "name": "OldSaveChar", "level": 1, "current_experience": 0,
            "current_hp": 15, "gold": 0, "equipment": {}
        }
        char = Character.from_dict(old_data)
        assert char.base_attack_stat == 1
        assert char.get_attack_power() == 1
