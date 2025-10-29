# Power Grid Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a tool to analyze power generation and consumption, showing generators, batteries, consumers, and calculating production vs consumption.

**Architecture:** Parse generator prefabs (Generator, HydroelectricGenerator, SteamTurbine2, SolarPanel, etc.), battery prefabs, extract Generator and Battery behavior data, identify powered consumers, calculate totals.

**Tech Stack:** Python 3.12+, oni-save-parser library, collections for grouping

---

## Task 1: Create Script and Identify Power Generators

**Files:**
- Create: `examples/power_info.py`
- Test: `tests/unit/test_power_info.py`

Follow same TDD pattern as previous tools:
1. Write failing help test
2. Create script skeleton  
3. Write test for finding generators
4. Implement generator detection
5. Commit each step

**Generator Prefabs to Detect:**
```python
GENERATOR_PREFABS = [
    "Generator",  # Coal generator
    "HydroelectricGenerator",  # Manual generator  
    "MethaneGenerator",  # Natural gas generator
    "PetroleumGenerator",  # Petroleum generator
    "HydrogenGenerator",  # Hydrogen generator
    "WoodGasGenerator",  # Ethanol distiller
    "SteamTurbine2",  # Steam turbine
    "SolarPanel",  # Solar panel
]
```

---

## Task 2: Add Battery Detection

**Step 1: Write test for battery detection**

```python
def test_power_info_finds_batteries(tmp_path: Path):
    """Should find batteries."""
    # Create save with Battery, BatteryMedium, BatterySmart
    # Test that script finds them
```

**Step 2: Implement battery detection**

```python
BATTERY_PREFABS = ["Battery", "BatteryMedium", "BatterySmart"]
```

---

## Task 3: Add Power Summary Output

Show totals:
- Number of generators by type
- Number of batteries
- Total generation capacity (if parsable from behaviors)
- Total battery capacity (if parsable from behaviors)

Add JSON output support.

---

## Task 4: Documentation and Testing

- Add error handling tests
- Update examples/README.md
- Update main README.md
- Update TOOLS_ROADMAP.md
- Verify all tests pass

---

## Future Enhancements

To complete power analysis, parse:
- **Generator behavior** - Extract wattage, fuel type, operational status
- **Battery behavior** - Extract charge level, capacity
- **EnergyConsumer behavior** - Identify powered buildings and consumption
- **CircuitManager** - Trace power grid circuits
- Calculate net power (generation - consumption)
