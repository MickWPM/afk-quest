import pytest
from src.enemy import Enemy

class TestEnemy:
    @pytest.fixture
    def sample_enemy(self):
        return Enemy(name="Goblin", max_hp=20, attack_stat=3, loot_gold_min=1, loot_gold_max=5)

    def test_enemy_creation(self, sample_enemy):
        assert sample_enemy.name == "Goblin"
        assert sample_enemy.max_hp == 20
        assert sample_enemy.current_hp == 20
        assert sample_enemy.attack_stat == 3
        assert sample_enemy.loot_gold_min == 1
        assert sample_enemy.loot_gold_max == 5
        assert not sample_enemy.is_dead

    def test_take_damage(self, sample_enemy):
        sample_enemy.take_damage(5)
        assert sample_enemy.current_hp == 15
        assert not sample_enemy.is_dead

    def test_take_damage_lethal(self, sample_enemy):
        sample_enemy.take_damage(20)
        assert sample_enemy.current_hp == 0
        assert sample_enemy.is_dead

    def test_take_damage_overkill(self, sample_enemy):
        sample_enemy.take_damage(100)
        assert sample_enemy.current_hp == 0
        assert sample_enemy.is_dead

    def test_take_zero_or_negative_damage(self, sample_enemy):
        initial_hp = sample_enemy.current_hp
        sample_enemy.take_damage(0)
        assert sample_enemy.current_hp == initial_hp
        sample_enemy.take_damage(-5)
        assert sample_enemy.current_hp == initial_hp

    def test_get_loot_gold(self, sample_enemy):
        for _ in range(20): # Test multiple times for randomness
            gold = sample_enemy.get_loot_gold()
            assert sample_enemy.loot_gold_min <= gold <= sample_enemy.loot_gold_max

    def test_get_loot_gold_min_equals_max(self):
        enemy = Enemy("FixedLoot", 10, 1, 5, 5)
        assert enemy.get_loot_gold() == 5

    def test_get_summary(self, sample_enemy):
        summary = sample_enemy.get_summary()
        assert "Goblin" in summary
        assert "HP: 20/20" in summary
        assert "Ready" in summary
        sample_enemy.take_damage(20)
        summary_dead = sample_enemy.get_summary()
        assert "Defeated" in summary_dead
        assert "HP: 0/20" in summary_dead
