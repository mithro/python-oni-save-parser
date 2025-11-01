"""Tests for output formatting functions."""
from oni_save_parser.formatters import (
    format_duplicant_compact,
    format_duration,
    format_geyser_compact,
    format_mass,
)


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


def test_format_geyser_compact():
    """Test compact geyser format."""
    stats = {
        "average_output_lifetime_kg_s": 2.1,
        "eruption_uptime_percent": 58.2,
        "active_uptime_percent": 72.0,
    }

    result = format_geyser_compact(
        prefab_name="Cool Steam Vent",
        index=0,
        position=(127.5, 147.0),
        element="Steam",
        temperature_c=136.9,
        stats=stats,
    )

    expected = (
        "Cool Steam Vent #1: 2.1 kg/s avg @ (127.5, 147.0) | "
        "58% erupting, 72% active | 136.9°C Steam"
    )
    assert result == expected


def test_format_duration_short():
    """Test duration formatting for short periods (< 1 cycle)."""
    result = format_duration(233.4)
    assert result == "233.4s (0.4 cycles)"


def test_format_duration_long():
    """Test duration formatting for long periods (>= 1 cycle)."""
    result = format_duration(58896.1)
    assert result == "98.2 cycles (58,896.1s)"


def test_format_mass_kg():
    """Test mass formatting in kilograms."""
    assert format_mass(486.0) == "486.0 kg"


def test_format_mass_tons():
    """Test mass formatting in tons."""
    assert format_mass(48100.0) == "48.1 t"
