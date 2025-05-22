import pytest
from src.enemy_manager import EnemyManager
from src.enemy import Enemy

@pytest.fixture
def sample_enemy_templates():
    return [
        {"name": "Rat", "hp": 5, "attack_stat": 1, "loot_gold_min": 0, "loot_gold_max": 1},
        {"name": "Wolf", "hp": 25, "attack_stat": 4, "loot_gold_min": 2, "loot_gold_max": 7},
    ]

@pytest.fixture
def empty_templates():
    return []

@pytest.fixture
def malformed_template():
    return [{"name": "BrokenBot", "health_points": 100}] # Missing 'hp', 'attack_stat' etc.


class TestEnemyManager:
    def test_enemy_manager_creation(self, sample_enemy_templates):
        manager = EnemyManager(enemy_templates=sample_enemy_templates)
        assert len(manager.enemy_templates) == 2

    def test_get_random_enemy(self, sample_enemy_templates):
        manager = EnemyManager(enemy_templates=sample_enemy_templates)
        enemy = manager.get_random_enemy()
        assert isinstance(enemy, Enemy)
        assert enemy.name in ["Rat", "Wolf"]

    def test_get_random_enemy_empty_templates(self, empty_templates, capsys):
        manager = EnemyManager(enemy_templates=empty_templates)
        enemy = manager.get_random_enemy()
        assert enemy is None
        captured = capsys.readouterr()
        assert "Error: No enemy templates available" in captured.out

    def test_get_random_enemy_malformed_template(self, malformed_template, capsys):
        # This test assumes random.choice picks the malformed one.
        # For more deterministic test, provide only the malformed template.
        manager = EnemyManager(enemy_templates=malformed_template)
        enemy = manager.get_random_enemy()
        assert enemy is None # Should fail to instantiate
        captured = capsys.readouterr()
        assert "Error: Enemy template is missing a required key" in captured.out

    def test_enemy_manager_creation_no_templates_warning(self, empty_templates, capsys):
        manager = EnemyManager(enemy_templates=empty_templates)
        captured = capsys.readouterr()
        assert "Warning: EnemyManager initialized with no enemy templates." in captured.out

