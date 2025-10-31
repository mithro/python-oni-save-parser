"""Tests for data extraction functions."""
import pytest
from oni_save_parser.extractors import extract_duplicant_skills


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
