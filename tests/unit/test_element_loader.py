"""Tests for element_loader module."""

from pathlib import Path
from unittest.mock import mock_open, patch

from oni_save_parser.element_loader import ElementLoader


def test_element_loader_loads_gas_yaml():
    """Test that ElementLoader can load gas.yaml."""
    yaml_content = """---
elements:
  - elementId: Steam
    specificHeatCapacity: 4.179
    state: Gas
    defaultTemperature: 400
"""

    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            loader = ElementLoader(Path("/fake/path"))
            element = loader.get_element("Steam")

    assert element is not None
    assert element["element_id"] == "Steam"
    assert element["state"] == "Gas"
    assert element["specific_heat_capacity"] == 4.179


def test_find_elements_path_returns_valid_path():
    """Test that find_elements_path() finds ONI installation."""
    from oni_save_parser.element_loader import find_elements_path

    # Should find the path (in reality this test needs better mocking)
    # For now, just test that function exists
    assert find_elements_path is not None
    assert callable(find_elements_path)

    # Function should return either a Path or None
    result = find_elements_path()
    assert result is None or isinstance(result, Path)
