"""Tests for output formatting functions."""
from oni_save_parser.formatters import format_duplicant_compact


def test_format_duplicant_compact_basic_info():
    """Test compact duplicant formatting."""
    duplicant_data = {
        "name": "Ashkan",
        "gender": "MALE",
        "position": (118.5, 191.0),
        "skills": {"Mining": 7, "Building": 5, "Farming": 2},
        "traits": ["QuickLearner", "Yokel", "MouthBreather"],
        "health": {"current": 85.0, "max": 100.0},
        "stress": {"current": 12.0, "max": 100.0}
    }

    result = format_duplicant_compact(duplicant_data)

    assert "Ashkan" in result
    assert "MALE" in result
    assert "Mining +7" in result or "Mining: 7" in result
    assert "QuickLearner" in result or "Quick Learner" in result
    assert "85" in result  # health value
    assert "12" in result  # stress value
