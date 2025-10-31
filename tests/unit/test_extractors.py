"""Tests for data extraction functions."""
import pytest
from oni_save_parser.extractors import extract_duplicant_skills
from oni_save_parser.extractors import extract_duplicant_traits


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
