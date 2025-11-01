"""Tests for fallback color palette."""
from oni_save_parser.assets.fallback_colors import FALLBACK_COLORS, get_fallback_color


def test_fallback_colors_contains_common_elements() -> None:
    """Test that fallback colors include common ONI elements."""
    assert "Oxygen" in FALLBACK_COLORS
    assert "Granite" in FALLBACK_COLORS
    assert "Water" in FALLBACK_COLORS
    assert "Sand" in FALLBACK_COLORS


def test_fallback_colors_are_rgb_tuples() -> None:
    """Test that all colors are valid RGB tuples."""
    for element, color in FALLBACK_COLORS.items():
        assert isinstance(color, tuple)
        assert len(color) == 3
        assert all(isinstance(c, int) for c in color)
        assert all(0 <= c <= 255 for c in color)


def test_get_fallback_color_known_element() -> None:
    """Test getting color for known element."""
    color = get_fallback_color("Oxygen")
    assert color == FALLBACK_COLORS["Oxygen"]


def test_get_fallback_color_unknown_element() -> None:
    """Test getting color for unknown element returns magenta."""
    color = get_fallback_color("UnknownElement123")
    assert color == (255, 0, 255)  # Magenta
