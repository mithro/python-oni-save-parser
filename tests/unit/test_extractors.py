"""Tests for data extraction functions."""
from pathlib import Path

import pytest

from oni_save_parser import get_game_objects_by_prefab, load_save_file
from oni_save_parser.extractors import (
    extract_attribute_levels,
    extract_duplicant_skills,
    extract_duplicant_traits,
    extract_geyser_stats,
    extract_health_status,
    get_geyser_config_from_prefab,
)


def test_extract_duplicant_skills_returns_dict() -> None:
    """Test that extract_duplicant_skills returns expected structure."""
    # Mock MinionResume behavior
    class MockBehavior:
        def __init__(self) -> None:
            self.name = "MinionResume"
            self.template_data = {
                "MasteryBySkillID": {"Mining": 7, "Building": 5},
                "AptitudeBySkillGroup": {"Mining": 3, "Building": 2},
                "currentRole": "Miner"
            }

    behavior = MockBehavior()
    result = extract_duplicant_skills(behavior)

    assert isinstance(result, dict)
    assert "mastery_by_skill" in result
    assert result["mastery_by_skill"]["Mining"] == 7


def test_extract_duplicant_traits_returns_list() -> None:
    """Test that extract_duplicant_traits returns trait names."""
    # Mock Klei.AI.Traits behavior
    class MockTrait:
        def __init__(self, trait_id: str) -> None:
            self.Name = trait_id

    class MockBehavior:
        def __init__(self) -> None:
            self.name = "Klei.AI.Traits"
            self.template_data = {
                "TraitList": [
                    MockTrait("QuickLearner"),
                    MockTrait("Yokel"),
                    MockTrait("MouthBreather")
                ]
            }

    behavior = MockBehavior()
    result = extract_duplicant_traits(behavior)

    assert isinstance(result, list)
    assert "QuickLearner" in result
    assert "Yokel" in result
    assert "MouthBreather" in result
    assert len(result) == 3


def test_extract_health_status_returns_dict() -> None:
    """Test that extract_health_status returns health state."""
    # Mock Health behavior
    class MockBehavior:
        def __init__(self) -> None:
            self.name = "Health"
            self.template_data = {
                "State": 0,  # Alive
                "CanBeIncapacitated": True
            }

    behavior = MockBehavior()
    result = extract_health_status(behavior)

    assert isinstance(result, dict)
    assert "state" in result
    assert result["state"] == "Alive"
    assert result["can_be_incapacitated"] is True


def test_extract_attribute_levels_returns_dict() -> None:
    """Test that extract_attribute_levels extracts health/stress values."""
    # Mock Klei.AI.AttributeLevels behavior
    class MockAttribute:
        def __init__(self, attribute_id: str, value: float, max_value: float) -> None:
            self.AttributeId = attribute_id
            self.experience = value
            self.experienceMax = max_value

    class MockBehavior:
        def __init__(self) -> None:
            self.name = "Klei.AI.AttributeLevels"
            self.template_data = {
                "saveLoadLevels": [
                    MockAttribute("HitPoints", 85.0, 100.0),
                    MockAttribute("Stress", 12.0, 100.0),
                    MockAttribute("QualityOfLife", 5.0, 100.0)
                ]
            }

    behavior = MockBehavior()
    result = extract_attribute_levels(behavior)

    assert isinstance(result, dict)
    assert result["HitPoints"]["current"] == 85.0
    assert result["HitPoints"]["max"] == 100.0
    assert result["Stress"]["current"] == 12.0


def test_extractors_with_real_save() -> None:
    """Test extractors with actual save file data."""
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        pytest.skip("Test save file not available")

    save = load_save_file(save_path)
    duplicants = get_game_objects_by_prefab(save, "Minion")

    assert len(duplicants) > 0, "No duplicants found in test save"

    dup = duplicants[0]

    # Find behaviors and extract data
    for behavior in dup.behaviors:
        if behavior.name == "MinionResume":
            skills = extract_duplicant_skills(behavior)
            assert isinstance(skills, dict)
            assert "mastery_by_skill" in skills

        elif behavior.name == "Klei.AI.Traits":
            traits = extract_duplicant_traits(behavior)
            assert isinstance(traits, list)

        elif behavior.name == "Health":
            health = extract_health_status(behavior)
            assert isinstance(health, dict)
            assert "state" in health

        elif behavior.name == "Klei.AI.AttributeLevels":
            attrs = extract_attribute_levels(behavior)
            assert isinstance(attrs, dict)


def test_extract_geyser_stats_calculates_rates() -> None:
    """Test geyser statistics extraction."""
    # Mock geyser configuration data
    config = {
        "scaledRate": 5.4,  # kg/s when erupting
        "scaledIterationLength": 401.1,  # total eruption cycle (s)
        "scaledIterationPercent": 0.582,  # fraction erupting
        "scaledYearLength": 81800.0,  # total dormancy cycle (s)
        "scaledYearPercent": 0.720,  # fraction active
    }

    stats = extract_geyser_stats(config)

    assert stats["emission_rate_kg_s"] == 5.4
    assert abs(stats["average_output_active_kg_s"] - 3.14) < 0.01  # 5.4 * 0.582
    assert abs(stats["average_output_lifetime_kg_s"] - 2.26) < 0.01  # 5.4 * 0.582 * 0.720


def test_extract_geyser_stats_with_thermal() -> None:
    """Test geyser thermal calculations with element data."""
    config = {
        "scaledRate": 5.4,
        "scaledIterationLength": 401.1,
        "scaledIterationPercent": 0.582,
        "scaledYearLength": 81800.0,
        "scaledYearPercent": 0.720,
    }

    element_data = {
        "specific_heat_capacity": 4.179,  # Steam SHC
    }

    temperature = 410.0  # Kelvin

    stats = extract_geyser_stats(config, element_data, temperature)

    # DTU = mass * SHC * temp, then convert to kDTU
    # Peak: 5.4 kg/s * 4.179 * 410 / 1000 = 9.25 kDTU/s (approximately)
    assert "peak_thermal_power_kdtu_s" in stats
    assert stats["peak_thermal_power_kdtu_s"] > 0


def test_get_geyser_config_from_prefab_known() -> None:
    """Test getting geyser config for known prefabs."""
    element_id, temp_k = get_geyser_config_from_prefab("GeyserGeneric_hot_water")
    assert element_id == "Water"
    assert temp_k == 368.15  # 95°C in Kelvin

    element_id, temp_k = get_geyser_config_from_prefab("GeyserGeneric_chlorine_gas")
    assert element_id == "ChlorineGas"
    assert temp_k == 333.15  # 60°C in Kelvin

    element_id, temp_k = get_geyser_config_from_prefab("GeyserGeneric_big_volcano")
    assert element_id == "Magma"
    assert temp_k == 2000.0


def test_get_geyser_config_from_prefab_unknown() -> None:
    """Test getting geyser config for unknown prefabs."""
    element_id, temp_k = get_geyser_config_from_prefab("UnknownGeyserType")
    assert element_id is None
    assert temp_k is None


def test_geyser_config_element_ids_valid() -> None:
    """Verify all element IDs in GEYSER_CONFIG exist in element loader."""
    from oni_save_parser.element_loader import get_global_element_loader
    from oni_save_parser.extractors import GEYSER_CONFIG

    loader = get_global_element_loader()
    if not loader:
        pytest.skip("Element loader not available (ONI not installed)")

    invalid_elements = []
    for prefab, (element_id, temp_k) in GEYSER_CONFIG.items():
        element = loader.get_element(element_id)
        if element is None:
            invalid_elements.append(f"{prefab}: '{element_id}' not found")

    assert not invalid_elements, "Invalid element IDs found:\n" + "\n".join(invalid_elements)


def test_geyser_config_temperature_ranges() -> None:
    """Verify temperatures are within physically reasonable ranges."""
    from oni_save_parser.extractors import GEYSER_CONFIG, MAX_GAME_TEMP_K, MIN_GAME_TEMP_K

    for prefab, (element_id, temp_k) in GEYSER_CONFIG.items():
        # Kelvin can't be below absolute zero
        assert temp_k > 0, f"{prefab} has impossible temperature: {temp_k}K"
        # Should be below 5000K (even metal volcanoes)
        assert temp_k < 5000, f"{prefab} temperature seems too high: {temp_k}K"
        # Should be reasonable for ONI game (typical gameplay range)
        assert MIN_GAME_TEMP_K <= temp_k <= MAX_GAME_TEMP_K, (
            f"{prefab} temperature outside typical range: {temp_k}K "
            f"(expected {MIN_GAME_TEMP_K}-{MAX_GAME_TEMP_K}K)"
        )
