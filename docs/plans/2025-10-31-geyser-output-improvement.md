# Geyser Output Improvement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform geyser_info.py from showing raw debug data to displaying gameplay-relevant statistics (output rates, storage requirements, thermal loads) with compact and detailed output formats.

**Architecture:** Follow extractor + formatter pattern. Add element_loader module to load ONI YAML files for element properties. Extract geyser stats in extractors.py, format in formatters.py, integrate in geyser_info.py.

**Tech Stack:** Python 3.12+, PyYAML for element data loading, pytest for testing

---

## Task 1: Element Loader - Setup and YAML Loading

**Files:**
- Create: `src/oni_save_parser/element_loader.py`
- Create: `tests/unit/test_element_loader.py`

**Step 1: Write failing test for element loader initialization**

Create `tests/unit/test_element_loader.py`:

```python
"""Tests for element_loader module."""

from pathlib import Path
from unittest.mock import patch, mock_open
import pytest
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_element_loader.py::test_element_loader_loads_gas_yaml -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'oni_save_parser.element_loader'"

**Step 3: Create element_loader module skeleton**

Create `src/oni_save_parser/element_loader.py`:

```python
"""Load and cache element properties from ONI game data files."""

from pathlib import Path
from typing import Any


class ElementLoader:
    """Loads element data from ONI YAML files."""

    def __init__(self, elements_path: Path) -> None:
        """Initialize element loader.

        Args:
            elements_path: Path to ONI StreamingAssets/elements directory
        """
        self._elements_path = elements_path
        self._elements_cache: dict[str, dict[str, Any]] = {}

    def get_element(self, element_id: str) -> dict[str, Any] | None:
        """Get element properties by ID.

        Args:
            element_id: Element ID (e.g., "Steam", "Water")

        Returns:
            Element properties dictionary or None if not found
        """
        return None  # Minimal implementation
```

**Step 4: Run test to verify it still fails (but differently)**

Run: `uv run pytest tests/unit/test_element_loader.py::test_element_loader_loads_gas_yaml -v`

Expected: FAIL with "AssertionError: assert None is not None"

**Step 5: Implement YAML loading**

Update `src/oni_save_parser/element_loader.py`:

```python
"""Load and cache element properties from ONI game data files."""

from pathlib import Path
from typing import Any
import yaml


class ElementLoader:
    """Loads element data from ONI YAML files."""

    def __init__(self, elements_path: Path) -> None:
        """Initialize element loader.

        Args:
            elements_path: Path to ONI StreamingAssets/elements directory
        """
        self._elements_path = elements_path
        self._elements_cache: dict[str, dict[str, Any]] = {}
        self._load_elements()

    def _load_elements(self) -> None:
        """Load all element data from YAML files."""
        for filename in ["gas.yaml", "liquid.yaml"]:
            filepath = self._elements_path / filename
            if filepath.exists():
                with open(filepath, "r") as f:
                    data = yaml.safe_load(f)
                    if data and "elements" in data:
                        for element in data["elements"]:
                            element_id = element.get("elementId")
                            if element_id:
                                self._elements_cache[element_id] = {
                                    "element_id": element_id,
                                    "state": element.get("state"),
                                    "specific_heat_capacity": element.get("specificHeatCapacity"),
                                    "max_mass": element.get("maxMass"),
                                }

    def get_element(self, element_id: str) -> dict[str, Any] | None:
        """Get element properties by ID.

        Args:
            element_id: Element ID (e.g., "Steam", "Water")

        Returns:
            Element properties dictionary or None if not found
        """
        return self._elements_cache.get(element_id)
```

**Step 6: Add PyYAML dependency**

Update `pyproject.toml` dependencies section:

```toml
dependencies = ["pyyaml>=6.0"]
```

**Step 7: Install dependencies**

Run: `uv sync`

Expected: PyYAML installed successfully

**Step 8: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_element_loader.py::test_element_loader_loads_gas_yaml -v`

Expected: PASS

**Step 9: Commit**

```bash
git add src/oni_save_parser/element_loader.py tests/unit/test_element_loader.py pyproject.toml
git commit -m "feat(element_loader): add YAML loading for element data"
```

---

## Task 2: Element Loader - Path Discovery

**Files:**
- Modify: `src/oni_save_parser/element_loader.py`
- Modify: `tests/unit/test_element_loader.py`

**Step 1: Write failing test for automatic path discovery**

Add to `tests/unit/test_element_loader.py`:

```python
from unittest.mock import patch


def test_find_elements_path_returns_valid_path():
    """Test that find_elements_path() finds ONI installation."""
    steam_path = Path("/home/user/.local/share/Steam/steamapps/common/OxygenNotIncluded")
    elements_path = steam_path / "OxygenNotIncluded_Data/StreamingAssets/elements"

    with patch("pathlib.Path.exists") as mock_exists:
        def exists_side_effect(path):
            return str(path) == str(elements_path)
        mock_exists.side_effect = lambda: exists_side_effect(mock_exists.call_args[0][0])

        from oni_save_parser.element_loader import find_elements_path
        result = find_elements_path()

    # Should find the path (in reality this test needs better mocking)
    # For now, just test that function exists
    assert find_elements_path is not None
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_element_loader.py::test_find_elements_path_returns_valid_path -v`

Expected: FAIL with "ImportError: cannot import name 'find_elements_path'"

**Step 3: Implement path discovery function**

Add to `src/oni_save_parser/element_loader.py`:

```python
import os
from pathlib import Path
from typing import Any
import yaml


def find_elements_path() -> Path | None:
    """Find ONI elements directory automatically.

    Searches common Steam installation locations.

    Returns:
        Path to elements directory or None if not found
    """
    search_paths = [
        Path.home() / ".local/share/Steam/steamapps/common/OxygenNotIncluded/OxygenNotIncluded_Data/StreamingAssets/elements",
        Path.home() / ".steam/steam/steamapps/common/OxygenNotIncluded/OxygenNotIncluded_Data/StreamingAssets/elements",
    ]

    # Check environment variable
    if "ONI_INSTALL_PATH" in os.environ:
        custom_path = Path(os.environ["ONI_INSTALL_PATH"]) / "OxygenNotIncluded_Data/StreamingAssets/elements"
        search_paths.insert(0, custom_path)

    for path in search_paths:
        if path.exists() and (path / "gas.yaml").exists():
            return path

    return None


def get_global_element_loader() -> ElementLoader | None:
    """Get a global ElementLoader instance with auto-discovered path.

    Returns:
        ElementLoader instance or None if elements path not found
    """
    elements_path = find_elements_path()
    if elements_path:
        return ElementLoader(elements_path)
    return None
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_element_loader.py::test_find_elements_path_returns_valid_path -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/element_loader.py tests/unit/test_element_loader.py
git commit -m "feat(element_loader): add automatic path discovery"
```

---

## Task 3: Element Loader - Error Handling

**Files:**
- Modify: `src/oni_save_parser/element_loader.py`
- Modify: `tests/unit/test_element_loader.py`

**Step 1: Write failing test for missing YAML files**

Add to `tests/unit/test_element_loader.py`:

```python
import logging


def test_element_loader_handles_missing_files(caplog):
    """Test graceful handling when YAML files don't exist."""
    with caplog.at_level(logging.WARNING):
        loader = ElementLoader(Path("/nonexistent/path"))
        element = loader.get_element("Steam")

    assert element is None
    assert "Element data files not found" in caplog.text or len(loader._elements_cache) == 0
```

**Step 2: Run test to verify current behavior**

Run: `uv run pytest tests/unit/test_element_loader.py::test_element_loader_handles_missing_files -v`

Expected: PASS (already handles missing files silently)

**Step 3: Add warning logging for missing files**

Update `src/oni_save_parser/element_loader.py` `_load_elements` method:

```python
import logging

logger = logging.getLogger(__name__)


class ElementLoader:
    # ... existing code ...

    def _load_elements(self) -> None:
        """Load all element data from YAML files."""
        files_loaded = 0

        for filename in ["gas.yaml", "liquid.yaml"]:
            filepath = self._elements_path / filename
            if filepath.exists():
                try:
                    with open(filepath, "r") as f:
                        data = yaml.safe_load(f)
                        if data and "elements" in data:
                            for element in data["elements"]:
                                element_id = element.get("elementId")
                                if element_id:
                                    self._elements_cache[element_id] = {
                                        "element_id": element_id,
                                        "state": element.get("state"),
                                        "specific_heat_capacity": element.get("specificHeatCapacity"),
                                        "max_mass": element.get("maxMass"),
                                    }
                    files_loaded += 1
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")

        if files_loaded == 0:
            logger.warning(
                f"Element data files not found at {self._elements_path}. "
                "Thermal calculations will be unavailable."
            )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_element_loader.py::test_element_loader_handles_missing_files -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/element_loader.py tests/unit/test_element_loader.py
git commit -m "feat(element_loader): add error handling and logging"
```

---

## Task 4: Geyser Extractor - Basic Statistics

**Files:**
- Modify: `src/oni_save_parser/extractors.py`
- Modify: `tests/unit/test_extractors.py`

**Step 1: Write failing test for extract_geyser_stats**

Add to `tests/unit/test_extractors.py`:

```python
from oni_save_parser.extractors import extract_geyser_stats


def test_extract_geyser_stats_calculates_rates():
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_extractors.py::test_extract_geyser_stats_calculates_rates -v`

Expected: FAIL with "ImportError: cannot import name 'extract_geyser_stats'"

**Step 3: Implement extract_geyser_stats function**

Add to `src/oni_save_parser/extractors.py`:

```python
def extract_geyser_stats(config: dict[str, Any]) -> dict[str, Any]:
    """Extract gameplay statistics from geyser configuration.

    Args:
        config: Geyser configuration dictionary from behavior template_data

    Returns:
        Dictionary with calculated geyser statistics
    """
    # Extract raw values
    emission_rate = config.get("scaledRate", 0.0)
    iteration_length = config.get("scaledIterationLength", 0.0)
    iteration_percent = config.get("scaledIterationPercent", 0.0)
    year_length = config.get("scaledYearLength", 0.0)
    year_percent = config.get("scaledYearPercent", 0.0)

    # Calculate rates
    avg_active = emission_rate * iteration_percent
    avg_lifetime = emission_rate * iteration_percent * year_percent

    # Calculate durations
    eruption_duration = iteration_length * iteration_percent
    idle_duration = iteration_length * (1 - iteration_percent)
    active_duration = year_length * year_percent
    dormant_duration = year_length * (1 - year_percent)

    # Calculate percentages
    eruption_uptime_percent = iteration_percent * 100
    active_uptime_percent = year_percent * 100
    overall_uptime_percent = iteration_percent * year_percent * 100

    # Calculate production amounts
    kg_per_eruption = emission_rate * eruption_duration
    kg_per_eruption_cycle = avg_active * iteration_length
    kg_per_active_period = avg_active * active_duration

    # Calculate storage requirements
    storage_idle = avg_active * idle_duration
    storage_dormancy = avg_lifetime * dormant_duration
    recommended_storage = max(storage_idle, storage_dormancy)

    return {
        # Rates
        "emission_rate_kg_s": emission_rate,
        "average_output_active_kg_s": avg_active,
        "average_output_lifetime_kg_s": avg_lifetime,

        # Eruption cycle
        "eruption_duration_s": eruption_duration,
        "idle_duration_s": idle_duration,
        "eruption_cycle_s": iteration_length,
        "eruption_uptime_percent": eruption_uptime_percent,

        # Dormancy cycle
        "active_duration_s": active_duration,
        "dormant_duration_s": dormant_duration,
        "dormancy_cycle_s": year_length,
        "active_uptime_percent": active_uptime_percent,

        # Overall
        "overall_uptime_percent": overall_uptime_percent,

        # Production amounts
        "kg_per_eruption": kg_per_eruption,
        "kg_per_eruption_cycle": kg_per_eruption_cycle,
        "kg_per_active_period": kg_per_active_period,

        # Storage requirements
        "storage_for_idle_kg": storage_idle,
        "storage_for_dormancy_kg": storage_dormancy,
        "recommended_storage_kg": recommended_storage,
    }
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_extractors.py::test_extract_geyser_stats_calculates_rates -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/extractors.py tests/unit/test_extractors.py
git commit -m "feat(extractors): add extract_geyser_stats function"
```

---

## Task 5: Geyser Extractor - Thermal Calculations

**Files:**
- Modify: `src/oni_save_parser/extractors.py`
- Modify: `tests/unit/test_extractors.py`

**Step 1: Write failing test for thermal calculations**

Add to `tests/unit/test_extractors.py`:

```python
def test_extract_geyser_stats_with_thermal():
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_extractors.py::test_extract_geyser_stats_with_thermal -v`

Expected: FAIL with "TypeError: extract_geyser_stats() takes 1 positional argument but 3 were given"

**Step 3: Update extract_geyser_stats signature and add thermal calculations**

Update in `src/oni_save_parser/extractors.py`:

```python
def extract_geyser_stats(
    config: dict[str, Any],
    element_data: dict[str, Any] | None = None,
    temperature_k: float | None = None,
) -> dict[str, Any]:
    """Extract gameplay statistics from geyser configuration.

    Args:
        config: Geyser configuration dictionary from behavior template_data
        element_data: Optional element properties (for thermal calculations)
        temperature_k: Optional output temperature in Kelvin

    Returns:
        Dictionary with calculated geyser statistics
    """
    # ... existing calculation code ...

    result = {
        # ... existing fields ...
    }

    # Add thermal calculations if data available
    if element_data and temperature_k:
        shc = element_data.get("specific_heat_capacity")
        if shc:
            # DTU = kg * SHC * temperature, convert to kDTU by dividing by 1000
            peak_thermal = emission_rate * shc * temperature_k / 1000
            avg_thermal = avg_lifetime * shc * temperature_k / 1000
            thermal_per_eruption = kg_per_eruption * shc * temperature_k / 1000

            result.update({
                "peak_thermal_power_kdtu_s": peak_thermal,
                "average_thermal_power_kdtu_s": avg_thermal,
                "thermal_per_eruption_kdtu": thermal_per_eruption,
            })

    return result
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_extractors.py::test_extract_geyser_stats_with_thermal -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/extractors.py tests/unit/test_extractors.py
git commit -m "feat(extractors): add thermal calculations to geyser stats"
```

---

## Task 6: Formatters - Compact Format

**Files:**
- Modify: `src/oni_save_parser/formatters.py`
- Modify: `tests/unit/test_formatters.py`

**Step 1: Write failing test for compact format**

Add to `tests/unit/test_formatters.py`:

```python
from oni_save_parser.formatters import format_geyser_compact


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

    expected = "Cool Steam Vent #1: 2.1 kg/s avg @ (127.5, 147.0) | 58% erupting, 72% active | 136.9°C Steam"
    assert result == expected
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_geyser_compact -v`

Expected: FAIL with "ImportError: cannot import name 'format_geyser_compact'"

**Step 3: Implement format_geyser_compact function**

Add to `src/oni_save_parser/formatters.py`:

```python
def format_geyser_compact(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    temperature_c: float,
    stats: dict[str, Any],
) -> str:
    """Format geyser information in compact one-line format.

    Args:
        prefab_name: Geyser type name
        index: Geyser index (0-based)
        position: (x, y) coordinates
        element: Element type (e.g., "Steam", "Natural Gas")
        temperature_c: Output temperature in Celsius
        stats: Statistics from extract_geyser_stats

    Returns:
        Formatted one-line string
    """
    avg_output = stats["average_output_lifetime_kg_s"]
    eruption_percent = stats["eruption_uptime_percent"]
    active_percent = stats["active_uptime_percent"]

    return (
        f"{prefab_name} #{index + 1}: {avg_output:.1f} kg/s avg @ "
        f"({position[0]}, {position[1]}) | "
        f"{eruption_percent:.0f}% erupting, {active_percent:.0f}% active | "
        f"{temperature_c:.1f}°C {element}"
    )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_geyser_compact -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/formatters.py tests/unit/test_formatters.py
git commit -m "feat(formatters): add format_geyser_compact function"
```

---

## Task 7: Formatters - Detailed Format Helper Functions

**Files:**
- Modify: `src/oni_save_parser/formatters.py`
- Modify: `tests/unit/test_formatters.py`

**Step 1: Write failing test for duration formatting**

Add to `tests/unit/test_formatters.py`:

```python
from oni_save_parser.formatters import format_duration


def test_format_duration_short():
    """Test duration formatting for short periods (< 1 cycle)."""
    result = format_duration(233.4)
    assert result == "233.4s (0.4 cycles)"


def test_format_duration_long():
    """Test duration formatting for long periods (>= 1 cycle)."""
    result = format_duration(58896.1)
    assert result == "98.2 cycles (58,896.1s)"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_duration_short -v`

Expected: FAIL with "ImportError: cannot import name 'format_duration'"

**Step 3: Implement duration formatting helper**

Add to `src/oni_save_parser/formatters.py`:

```python
def format_duration(seconds: float) -> str:
    """Format duration in seconds and cycles.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string with seconds and cycles
    """
    cycles = seconds / 600.0  # 1 cycle = 600 seconds

    if cycles < 1.0:
        return f"{seconds:.1f}s ({cycles:.1f} cycles)"
    else:
        return f"{cycles:.1f} cycles ({seconds:,.1f}s)"


def format_mass(kg: float) -> str:
    """Format mass in kg or tons.

    Args:
        kg: Mass in kilograms

    Returns:
        Formatted string with appropriate unit
    """
    if kg >= 1000:
        return f"{kg / 1000:.1f} t"
    else:
        return f"{kg:.1f} kg"
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_duration_short tests/unit/test_formatters.py::test_format_duration_long -v`

Expected: PASS

**Step 5: Write test for mass formatting**

Add to `tests/unit/test_formatters.py`:

```python
from oni_save_parser.formatters import format_mass


def test_format_mass_kg():
    """Test mass formatting in kilograms."""
    assert format_mass(486.0) == "486.0 kg"


def test_format_mass_tons():
    """Test mass formatting in tons."""
    assert format_mass(48100.0) == "48.1 t"
```

**Step 6: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_mass_kg tests/unit/test_formatters.py::test_format_mass_tons -v`

Expected: PASS

**Step 7: Commit**

```bash
git add src/oni_save_parser/formatters.py tests/unit/test_formatters.py
git commit -m "feat(formatters): add duration and mass formatting helpers"
```

---

## Task 8: Formatters - Detailed Format (Part 1: Header and Rates)

**Files:**
- Modify: `src/oni_save_parser/formatters.py`
- Modify: `tests/unit/test_formatters.py`

**Step 1: Write failing test for detailed format header**

Add to `tests/unit/test_formatters.py`:

```python
from oni_save_parser.formatters import format_geyser_detailed


def test_format_geyser_detailed_header():
    """Test detailed format header section."""
    stats = {
        "average_output_lifetime_kg_s": 2.1,
        "average_output_active_kg_s": 2.9,
        "emission_rate_kg_s": 5.4,
        "eruption_uptime_percent": 58.2,
        "active_uptime_percent": 72.0,
        "overall_uptime_percent": 41.9,
        "eruption_duration_s": 233.4,
        "idle_duration_s": 167.7,
        "eruption_cycle_s": 401.1,
        "active_duration_s": 58896.1,
        "dormant_duration_s": 22903.9,
        "dormancy_cycle_s": 81800.0,
        "kg_per_eruption": 1260.0,
        "kg_per_active_period": 170800.0,
        "storage_for_idle_kg": 486.0,
        "storage_for_dormancy_kg": 48100.0,
        "recommended_storage_kg": 48100.0,
    }

    result = format_geyser_detailed(
        prefab_name="Cool Steam Vent",
        index=0,
        position=(127.5, 147.0),
        element="Steam",
        element_state="Gas",
        temperature_c=136.9,
        stats=stats,
    )

    assert "=== Cool Steam Vent #1 ===" in result
    assert "Position:" in result
    assert "(127.5, 147.0)" in result
    assert "Output Element:" in result
    assert "Steam (Gas)" in result
    assert "Output Temp:" in result
    assert "136.9°C" in result
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_geyser_detailed_header -v`

Expected: FAIL with "ImportError: cannot import name 'format_geyser_detailed'"

**Step 3: Implement format_geyser_detailed skeleton**

Add to `src/oni_save_parser/formatters.py`:

```python
def format_geyser_detailed(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    element_state: str,
    temperature_c: float,
    stats: dict[str, Any],
    thermal_stats: dict[str, Any] | None = None,
) -> str:
    """Format geyser information in detailed multi-line format.

    Args:
        prefab_name: Geyser type name
        index: Geyser index (0-based)
        position: (x, y) coordinates
        element: Element type (e.g., "Steam", "Natural Gas")
        element_state: "Gas" or "Liquid"
        temperature_c: Output temperature in Celsius
        stats: Statistics from extract_geyser_stats
        thermal_stats: Optional thermal statistics

    Returns:
        Formatted multi-line string
    """
    lines = []

    # Header
    lines.append(f"=== {prefab_name} #{index + 1} ===")
    lines.append(f"Position:         ({position[0]}, {position[1]})")
    lines.append(f"Output Element:   {element} ({element_state})")
    lines.append(f"Output Temp:      {temperature_c:.1f}°C")
    lines.append("")

    # Output Rates
    lines.append("Output Rates:")
    lines.append(f"  Average (lifetime):        {stats['average_output_lifetime_kg_s']:.1f} kg/s  (accounts for all downtime)")
    lines.append(f"  Average (when active):     {stats['average_output_active_kg_s']:.1f} kg/s  (during active period only)")
    lines.append(f"  Peak (when erupting):      {stats['emission_rate_kg_s']:.1f} kg/s  (maximum output rate)")
    lines.append("")

    return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_geyser_detailed_header -v`

Expected: PASS

**Step 5: Commit**

```bash
git add src/oni_save_parser/formatters.py tests/unit/test_formatters.py
git commit -m "feat(formatters): add detailed format header and rates"
```

---

## Task 9: Formatters - Detailed Format (Part 2: Thermal and Eruption)

**Files:**
- Modify: `src/oni_save_parser/formatters.py`

**Step 1: Add thermal and eruption sections to format_geyser_detailed**

Update `format_geyser_detailed` in `src/oni_save_parser/formatters.py`:

```python
def format_geyser_detailed(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    element_state: str,
    temperature_c: float,
    stats: dict[str, Any],
    thermal_stats: dict[str, Any] | None = None,
) -> str:
    """Format geyser information in detailed multi-line format."""
    lines = []

    # Header
    lines.append(f"=== {prefab_name} #{index + 1} ===")
    lines.append(f"Position:         ({position[0]}, {position[1]})")
    lines.append(f"Output Element:   {element} ({element_state})")
    lines.append(f"Output Temp:      {temperature_c:.1f}°C")
    lines.append("")

    # Output Rates
    lines.append("Output Rates:")
    lines.append(f"  Average (lifetime):        {stats['average_output_lifetime_kg_s']:.1f} kg/s  (accounts for all downtime)")
    lines.append(f"  Average (when active):     {stats['average_output_active_kg_s']:.1f} kg/s  (during active period only)")
    lines.append(f"  Peak (when erupting):      {stats['emission_rate_kg_s']:.1f} kg/s  (maximum output rate)")
    lines.append("")

    # Thermal Output (if available)
    if thermal_stats:
        peak_thermal = thermal_stats.get("peak_thermal_power_kdtu_s", 0)
        avg_thermal = thermal_stats.get("average_thermal_power_kdtu_s", 0)
        thermal_eruption = thermal_stats.get("thermal_per_eruption_kdtu", 0)

        lines.append("Thermal Output:")
        lines.append(f"  Peak thermal power:          {peak_thermal:>7.1f} kDTU/s  (when erupting)")
        lines.append(f"  Average thermal power:       {avg_thermal:>7.1f} kDTU/s  (lifetime average)")
        lines.append(f"  Total heat per eruption: {thermal_eruption:>11,.1f} kDTU    (over {format_duration(stats['eruption_duration_s'])})")
        lines.append("")

    # Eruption Cycle
    lines.append("Eruption Cycle (short-term):")

    erupting_dur = format_duration(stats["eruption_duration_s"])
    idle_dur = format_duration(stats["idle_duration_s"])
    cycle_dur = format_duration(stats["eruption_cycle_s"])

    kg_eruption = format_mass(stats["kg_per_eruption"])
    thermal_eruption_str = ""
    if thermal_stats:
        thermal_eruption_str = f" @ {thermal_stats.get('thermal_per_eruption_kdtu', 0):>11,.0f} kDTU"

    lines.append(f"  Erupting:    {erupting_dur:>20}  → Produces {kg_eruption:>8}{thermal_eruption_str}")
    lines.append(f"  Idle:        {idle_dur:>20}  → Produces    0.0 kg")
    lines.append(f"  Total cycle: {cycle_dur:>20}")
    lines.append(f"  Uptime:      {stats['eruption_uptime_percent']:>6.1f}%")
    lines.append("")

    # Storage for idle
    storage_idle = format_mass(stats["storage_for_idle_kg"])
    lines.append(f"  Storage for idle period: {storage_idle}")

    # Calculate reservoir count
    if element_state == "Gas":
        reservoir_capacity = 1000  # Gas Reservoir
        reservoir_count = int(stats["storage_for_idle_kg"] / reservoir_capacity) + (1 if stats["storage_for_idle_kg"] % reservoir_capacity > 0 else 0)
        lines.append(f"    - {reservoir_count} Gas Reservoir{'s' if reservoir_count != 1 else ''} (1,000 kg each)")

    lines.append("")

    return "\n".join(lines)
```

**Step 2: Test manually**

Run: `uv run pytest tests/unit/test_formatters.py::test_format_geyser_detailed_header -v`

Expected: PASS (function extended but existing test still passes)

**Step 3: Commit**

```bash
git add src/oni_save_parser/formatters.py
git commit -m "feat(formatters): add thermal and eruption cycle to detailed format"
```

---

## Task 10: Formatters - Detailed Format (Part 3: Dormancy and Completion)

**Files:**
- Modify: `src/oni_save_parser/formatters.py`

**Step 1: Add dormancy section to format_geyser_detailed**

Continue updating `format_geyser_detailed` in `src/oni_save_parser/formatters.py`:

```python
def format_geyser_detailed(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    element_state: str,
    temperature_c: float,
    stats: dict[str, Any],
    thermal_stats: dict[str, Any] | None = None,
    element_max_mass: float | None = None,
) -> str:
    """Format geyser information in detailed multi-line format.

    Args:
        prefab_name: Geyser type name
        index: Geyser index (0-based)
        position: (x, y) coordinates
        element: Element type
        element_state: "Gas" or "Liquid"
        temperature_c: Output temperature in Celsius
        stats: Statistics from extract_geyser_stats
        thermal_stats: Optional thermal statistics
        element_max_mass: Optional max kg per tile (for liquids)

    Returns:
        Formatted multi-line string
    """
    lines = []

    # ... existing header, rates, thermal, eruption code ...

    # Dormancy Cycle
    lines.append("Dormancy Cycle (long-term):")

    active_dur = format_duration(stats["active_duration_s"])
    dormant_dur = format_duration(stats["dormant_duration_s"])
    dormancy_cycle_dur = format_duration(stats["dormancy_cycle_s"])

    kg_active = format_mass(stats["kg_per_active_period"])
    thermal_active_str = ""
    if thermal_stats and "thermal_per_eruption_kdtu" in thermal_stats:
        # Total thermal during active period
        num_eruptions = stats["active_duration_s"] / stats["eruption_cycle_s"]
        total_thermal_active = thermal_stats["thermal_per_eruption_kdtu"] * num_eruptions
        thermal_active_str = f" @ {total_thermal_active:>11,.0f} kDTU"

    lines.append(f"  Active:      {active_dur:>28}  → Produces {kg_active:>8}{thermal_active_str}")
    lines.append(f"  Dormant:     {dormant_dur:>28}  → Produces    0.0 kg")
    lines.append(f"  Total cycle: {dormancy_cycle_dur:>28}")
    lines.append(f"  Uptime:      {stats['active_uptime_percent']:>6.1f}%")
    lines.append("")

    # Storage for dormancy
    storage_dormancy = format_mass(stats["storage_for_dormancy_kg"])
    lines.append(f"  Storage for dormancy: {storage_dormancy}")

    # Calculate reservoir and tile storage
    if element_state == "Gas":
        reservoir_capacity = 1000
        reservoir_count = int(stats["storage_for_dormancy_kg"] / reservoir_capacity) + (1 if stats["storage_for_dormancy_kg"] % reservoir_capacity > 0 else 0)
        lines.append(f"    - {reservoir_count} Gas Reservoir{'s' if reservoir_count != 1 else ''} (1,000 kg each)")
    else:  # Liquid
        reservoir_capacity = 5000
        reservoir_count = int(stats["storage_for_dormancy_kg"] / reservoir_capacity) + (1 if stats["storage_for_dormancy_kg"] % reservoir_capacity > 0 else 0)
        lines.append(f"    - {reservoir_count} Liquid Reservoir{'s' if reservoir_count != 1 else ''} (5,000 kg each)")
        if element_max_mass:
            tile_count = int(stats["storage_for_dormancy_kg"] / element_max_mass) + (1 if stats["storage_for_dormancy_kg"] % element_max_mass > 0 else 0)
            lines.append(f"    - {tile_count} tiles @ {element_max_mass:,.0f} kg/tile max")

    lines.append("")

    # Overall summary
    lines.append(f"Overall Uptime: {stats['overall_uptime_percent']:.1f}% ({stats['eruption_uptime_percent']:.1f}% erupting × {stats['active_uptime_percent']:.1f}% active)")
    lines.append("")

    # Recommended storage
    recommended = format_mass(stats["recommended_storage_kg"])
    buffer_type = "dormancy" if stats["storage_for_dormancy_kg"] > stats["storage_for_idle_kg"] else "idle"
    lines.append(f"Recommended minimum storage: {recommended} ({buffer_type} buffer dominates)")

    return "\n".join(lines)
```

**Step 2: Test manually with example**

Create a quick test script to verify output looks correct. No automated test needed here.

**Step 3: Commit**

```bash
git add src/oni_save_parser/formatters.py
git commit -m "feat(formatters): complete detailed format with dormancy and storage"
```

---

## Task 11: Update geyser_info.py - Add Format Flag

**Files:**
- Modify: `examples/geyser_info.py`

**Step 1: Add --format flag to argument parser**

Update the argument parser in `examples/geyser_info.py`:

```python
parser.add_argument(
    "--format",
    choices=["compact", "detailed"],
    default="detailed",
    help="Output format (default: detailed)",
)
```

**Step 2: Test argument parsing**

Run: `uv run python examples/geyser_info.py --help`

Expected: Help text shows new --format option

**Step 3: Commit**

```bash
git add examples/geyser_info.py
git commit -m "feat(geyser_info): add --format flag for output selection"
```

---

## Task 12: Update geyser_info.py - Integrate Element Loader

**Files:**
- Modify: `examples/geyser_info.py`

**Step 1: Import element loader at top of file**

Add to imports in `examples/geyser_info.py`:

```python
from oni_save_parser.element_loader import get_global_element_loader
```

**Step 2: Initialize element loader in main()**

Add after argument parsing:

```python
def main():
    args = parser.parse_args()

    # Initialize element loader
    element_loader = get_global_element_loader()
    if element_loader is None and not args.debug:
        print("Warning: Could not find ONI element data. Thermal calculations unavailable.", file=sys.stderr)
```

**Step 3: Test that it runs without errors**

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav --list-prefabs`

Expected: Runs successfully, shows prefab list

**Step 4: Commit**

```bash
git add examples/geyser_info.py
git commit -m "feat(geyser_info): integrate element loader"
```

---

## Task 13: Update geyser_info.py - Use Extractors and Formatters

**Files:**
- Modify: `examples/geyser_info.py`

**Step 1: Import extractors and formatters**

Add to imports:

```python
from oni_save_parser.extractors import extract_geyser_stats
from oni_save_parser.formatters import format_geyser_compact, format_geyser_detailed
```

**Step 2: Update main loop to use new functions**

Replace the section that prints geyser info with:

```python
# Process each geyser prefab type
for prefab_name in geyser_prefabs:
    geysers = get_game_objects_by_prefab(save, prefab_name)

    print(f"\n{'=' * 60}")
    print(f"{prefab_name}: {len(geysers)} found")
    print('=' * 60)

    for i, geyser in enumerate(geysers):
        # Extract basic info
        info = extract_geyser_info(geyser)
        position = (geyser.position.x, geyser.position.y)

        # Find geyser configuration and element info
        config = None
        element_id = None
        temperature_k = None

        for behavior in geyser.behaviors:
            if behavior.name == "Geyser" and behavior.template_data:
                config_dict = behavior.template_data.get("configuration", {})
                if isinstance(config_dict, dict):
                    config = config_dict

            if behavior.name == "ElementEmitter" and behavior.template_data:
                element_id = behavior.template_data.get("emittedElement")

            if behavior.name == "Temperature" and behavior.template_data:
                temperature_k = behavior.template_data.get("value")

        # Skip if no geyser configuration
        if not config:
            if args.debug:
                print(f"\n=== {prefab_name} #{i + 1} ===")
                print(f"Position: {position}")
                print("Status: Not analyzed or no Geyser behavior")
            continue

        # Extract statistics
        element_data = None
        if element_loader and element_id:
            element_data = element_loader.get_element(element_id)

        stats = extract_geyser_stats(config, element_data, temperature_k)

        # Get element info for formatting
        element_name = element_id or "Unknown"
        element_state = "Gas"
        element_max_mass = None
        temperature_c = (temperature_k - 273.15) if temperature_k else 0

        if element_data:
            element_state = element_data.get("state", "Gas")
            element_max_mass = element_data.get("max_mass")

        # Format output
        if args.format == "compact":
            output = format_geyser_compact(
                prefab_name=prefab_name,
                index=i,
                position=position,
                element=element_name,
                temperature_c=temperature_c,
                stats=stats,
            )
            print(output)
        else:  # detailed
            # Extract thermal stats if available
            thermal_stats = {}
            if "peak_thermal_power_kdtu_s" in stats:
                thermal_stats = {
                    "peak_thermal_power_kdtu_s": stats["peak_thermal_power_kdtu_s"],
                    "average_thermal_power_kdtu_s": stats["average_thermal_power_kdtu_s"],
                    "thermal_per_eruption_kdtu": stats["thermal_per_eruption_kdtu"],
                }

            output = format_geyser_detailed(
                prefab_name=prefab_name,
                index=i,
                position=position,
                element=element_name,
                element_state=element_state,
                temperature_c=temperature_c,
                stats=stats,
                thermal_stats=thermal_stats if thermal_stats else None,
                element_max_mass=element_max_mass,
            )
            print(output)

        # Show debug info if requested
        if args.debug:
            print("\nDEBUG - Raw Configuration:")
            print(f"  {config}")
```

**Step 3: Test on a save file**

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav --format compact | head -20`

Expected: Shows compact format output

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav | head -50`

Expected: Shows detailed format output

**Step 4: Commit**

```bash
git add examples/geyser_info.py
git commit -m "feat(geyser_info): use extractors and formatters for output"
```

---

## Task 14: Integration Testing

**Files:**
- Run: Various test commands

**Step 1: Run full test suite**

Run: `uv run pytest -v`

Expected: All tests pass (240+ tests)

**Step 2: Test geyser_info.py on all test saves**

Run:
```bash
for save in test_saves/*.sav; do
    echo "=== Testing: $save ==="
    uv run python examples/geyser_info.py "$save" --format compact | head -5
done
```

Expected: All saves process without errors

**Step 3: Test --skip-vents with both formats**

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav --skip-vents --format compact`

Expected: Vents filtered out, only geysers shown

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav --skip-vents --format detailed | head -50`

Expected: Detailed output without vents

**Step 4: Test --debug flag**

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav --debug | head -80`

Expected: Shows detailed output plus DEBUG sections with raw configuration

**Step 5: Create integration test if all manual tests pass**

If everything works, document test commands in commit message.

**Step 6: Commit test verification**

```bash
git commit --allow-empty -m "test: verify geyser_info.py integration with all formats"
```

---

## Task 15: Fix Alignment Issues

**Files:**
- Modify: `src/oni_save_parser/formatters.py`

**Step 1: Review actual output for alignment issues**

Run: `uv run python examples/geyser_info.py test_saves/02-mid-game-cycle-148.sav | head -60`

Check that:
- Numbers in "Output Rates" section align
- Numbers in "Thermal Output" section align
- Parentheses in duration lines align
- Production amounts align with arrows

**Step 2: Fix any alignment issues found**

Adjust field widths and spacing in `format_geyser_detailed()` as needed.

Common fixes:
- Use f-string right-alignment: `{value:>width.precision}`
- Ensure consistent spacing before parentheses
- Make sure arrow symbols (→) are at same column

**Step 3: Re-test alignment**

Run the same command and verify alignment is correct.

**Step 4: Commit if changes made**

```bash
git add src/oni_save_parser/formatters.py
git commit -m "fix(formatters): improve alignment in detailed output"
```

---

## Task 16: Update Tests for geyser_info.py

**Files:**
- Modify: `tests/unit/test_geyser_info.py`

**Step 1: Review existing geyser_info tests**

Read: `tests/unit/test_geyser_info.py`

Check what's already tested.

**Step 2: Add test for compact format output**

Add test if not already present:

```python
def test_geyser_info_compact_format(tmp_path):
    """Test geyser_info.py with compact format."""
    # Use smallest test save
    save_path = Path("test_saves/01-early-game-cycle-010.sav")
    if not save_path.exists():
        pytest.skip("Test save not found")

    result = subprocess.run(
        ["uv", "run", "python", "examples/geyser_info.py", str(save_path), "--format", "compact"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "kg/s avg" in result.stdout
    assert "erupting" in result.stdout
```

**Step 3: Run new test**

Run: `uv run pytest tests/unit/test_geyser_info.py::test_geyser_info_compact_format -v`

Expected: PASS

**Step 4: Commit**

```bash
git add tests/unit/test_geyser_info.py
git commit -m "test(geyser_info): add test for compact format"
```

---

## Task 17: Documentation Updates

**Files:**
- Modify: `README.md`
- Modify: `examples/geyser_info.py` (docstring)

**Step 1: Update geyser_info.py docstring**

Update the module docstring at top of `examples/geyser_info.py`:

```python
"""Extract and display geyser information from ONI save files.

This script loads a save file and prints detailed information about all geysers,
including:
- Output rates (peak, active average, lifetime average)
- Eruption and dormancy cycle timing
- Storage requirements for idle and dormant periods
- Thermal output (if ONI element data available)

Supports two output formats:
- Compact: One-line summary per geyser
- Detailed: Full breakdown with all planning information

Usage:
    python geyser_info.py SAVE_PATH [--format compact|detailed] [--skip-vents] [--debug]

Examples:
    # Detailed format (default)
    python geyser_info.py save.sav

    # Compact one-line summaries
    python geyser_info.py save.sav --format compact

    # Skip vents, show only geysers
    python geyser_info.py save.sav --skip-vents

    # Show raw debug data
    python geyser_info.py save.sav --debug
"""
```

**Step 2: Update README.md**

Add to README.md in the examples section:

```markdown
### Geyser Information

Extract detailed geyser statistics including output rates, timing, storage requirements, and thermal loads:

```bash
# Detailed format with all planning information
python examples/geyser_info.py save.sav

# Compact one-line summaries
python examples/geyser_info.py save.sav --format compact

# Skip vents, show only actual geysers
python examples/geyser_info.py save.sav --skip-vents
```

The detailed format includes:
- Output rates (peak, active average, lifetime average)
- Eruption and dormancy cycle timing
- Storage requirements for idle and dormant periods
- Thermal output calculations (requires ONI installation)
```

**Step 3: Commit**

```bash
git add README.md examples/geyser_info.py
git commit -m "docs: update geyser_info.py documentation"
```

---

## Task 18: Final Testing and Cleanup

**Files:**
- Run: Various test commands

**Step 1: Run full test suite one more time**

Run: `uv run pytest -v`

Expected: All tests pass

**Step 2: Run type checking**

Run: `uv run mypy src/oni_save_parser`

Expected: No type errors (or acceptable errors only)

**Step 3: Run linting**

Run: `uv run ruff check src/oni_save_parser examples/geyser_info.py`

Expected: No errors or only minor warnings

**Step 4: Fix any linting issues**

If ruff reports issues, fix them:

Run: `uv run ruff check --fix src/oni_save_parser examples/geyser_info.py`

**Step 5: Test on all save files with both formats**

Run:
```bash
for save in test_saves/*.sav; do
    echo "=== Compact: $save ==="
    uv run python examples/geyser_info.py "$save" --format compact --skip-vents | head -10
    echo "=== Detailed: $save ==="
    uv run python examples/geyser_info.py "$save" --format detailed --skip-vents | head -40
done
```

Expected: All saves work with both formats

**Step 6: Commit any fixes**

```bash
git add -A
git commit -m "fix: address linting and type checking issues"
```

---

## Completion

After all tasks complete:

1. **Verify final state:**
   - All tests pass: `uv run pytest`
   - Type checking clean: `uv run mypy src/oni_save_parser`
   - Linting clean: `uv run ruff check src/oni_save_parser`

2. **Review changes:**
   ```bash
   git log --oneline
   git diff main
   ```

3. **Ready for code review and merge:**
   - Feature complete per design document
   - All tests passing
   - Documentation updated
   - Clean commit history

**Next steps:** Use superpowers:finishing-a-development-branch to merge or create PR.
