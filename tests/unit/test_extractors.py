"""Tests for data extraction functions."""
import pytest
from oni_save_parser.extractors import extract_duplicant_skills
from oni_save_parser.extractors import extract_duplicant_traits
from oni_save_parser.extractors import extract_health_status
from oni_save_parser.extractors import extract_attribute_levels


def test_extract_duplicant_skills_returns_dict():
    """Test that extract_duplicant_skills returns expected structure."""
    # Mock MinionResume behavior
    class MockBehavior:
        def __init__(self):
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


def test_extract_duplicant_traits_returns_list():
    """Test that extract_duplicant_traits returns trait names."""
    # Mock Klei.AI.Traits behavior
    class MockTrait:
        def __init__(self, trait_id):
            self.Name = trait_id

    class MockBehavior:
        def __init__(self):
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


def test_extract_health_status_returns_dict():
    """Test that extract_health_status returns health state."""
    # Mock Health behavior
    class MockBehavior:
        def __init__(self):
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


def test_extract_attribute_levels_returns_dict():
    """Test that extract_attribute_levels extracts health/stress values."""
    # Mock Klei.AI.AttributeLevels behavior
    class MockAttribute:
        def __init__(self, attribute_id, value, max_value):
            self.AttributeId = attribute_id
            self.experience = value
            self.experienceMax = max_value

    class MockBehavior:
        def __init__(self):
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
