# Geyser Output Improvement Design

**Date:** 2025-10-31
**Status:** Design Complete - Ready for Implementation

## Problem Statement

The current `geyser_info.py` output shows raw internal data (like `rateRoll`, `iterationLengthRoll`, etc.) that is not useful for gameplay planning. Players need actionable information to design cooling systems, storage capacity, and resource management.

**Current Output (Not Useful):**
```
=== GeyserGeneric_slimy_po2 #1 ===
Position: (127.5, 147.0)

Geyser State:
  configuration: {'typeId': {'hash': 2128532496}, 'rateRoll': 0.6563429832458496, ...}
```

## Design Goals

1. **Hide raw debug data** - Move internal configuration to `--debug` flag only
2. **Show gameplay-relevant information** - Output rates, timing, storage requirements, thermal loads
3. **Support multiple output formats** - Compact one-line summaries and detailed breakdowns
4. **Use game data** - Load element properties from ONI YAML files for accuracy
5. **Maintain consistency** - Follow the extractor + formatter pattern used by duplicant_info.py

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     geyser_info.py (CLI)                    │
│  - Parse arguments (--format, --debug, --skip-vents)       │
│  - Load save file and find geysers                         │
│  - Call extractors and formatters                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
┌─────────────────┐   ┌──────────────────┐
│   extractors.py │   │   formatters.py   │
│                 │   │                   │
│ extract_geyser_ │   │ format_geyser_   │
│   stats()       │   │   compact()       │
│                 │   │ format_geyser_   │
│                 │   │   detailed()      │
└────────┬────────┘   └──────────────────┘
         │
         ▼
┌──────────────────┐
│ element_loader.py│
│  (NEW MODULE)    │
│                  │
│ - Load YAML      │
│ - Cache elements │
│ - Lookup props   │
└──────────────────┘
```

### Module Responsibilities

**`oni_save_parser/extractors.py`:**
- Add `extract_geyser_stats()` function
- Extract and calculate gameplay statistics from geyser behavior data
- Returns structured dictionary with rates, timing, storage requirements

**`oni_save_parser/formatters.py`:**
- Add `format_geyser_compact()` - One-line summary
- Add `format_geyser_detailed()` - Full breakdown with alignment
- Format durations, storage, and thermal output

**`oni_save_parser/element_loader.py` (NEW):**
- Load element data from ONI YAML files
- Cache parsed element properties
- Provide lookup functions for element properties

**`examples/geyser_info.py`:**
- Update to use new extractors and formatters
- Add `--format` flag for compact/detailed output
- Keep existing `--debug`, `--skip-vents`, `--list-prefabs` flags

## Data Flow

### Geyser Statistics Extraction

The `extract_geyser_stats()` function processes the "Geyser" behavior template_data:

**Input:** Geyser behavior with configuration containing:
- `scaledRate` - Emission rate in kg/s when erupting
- `scaledIterationLength` - Total eruption cycle time (s)
- `scaledIterationPercent` - Fraction of cycle spent erupting (0-1)
- `scaledYearLength` - Total dormancy cycle time (s)
- `scaledYearPercent` - Fraction of year spent active (0-1)

**Output:** Dictionary with calculated values:
```python
{
    # Rates
    "emission_rate_kg_s": float,              # Peak rate when erupting
    "average_output_active_kg_s": float,      # Average during active period
    "average_output_lifetime_kg_s": float,    # Average accounting for dormancy

    # Eruption cycle (short-term)
    "eruption_duration_s": float,             # Time spent erupting
    "idle_duration_s": float,                 # Time spent idle
    "eruption_cycle_s": float,                # Total eruption cycle
    "eruption_uptime_percent": float,         # % of cycle erupting

    # Dormancy cycle (long-term)
    "active_duration_s": float,               # Time spent active
    "dormant_duration_s": float,              # Time spent dormant
    "dormancy_cycle_s": float,                # Total dormancy cycle
    "active_uptime_percent": float,           # % of year active

    # Overall
    "overall_uptime_percent": float,          # eruption% × active%

    # Production amounts
    "kg_per_eruption": float,                 # Total kg per eruption burst
    "kg_per_eruption_cycle": float,           # Total kg per full eruption cycle
    "kg_per_active_period": float,            # Total kg during active period

    # Storage requirements
    "storage_for_idle_kg": float,             # Buffer needed for idle period
    "storage_for_dormancy_kg": float,         # Buffer needed for dormancy
    "recommended_storage_kg": float,          # max(idle, dormancy) buffer

    # Thermal (if element data available)
    "peak_thermal_power_kdtu_s": float,       # kDTU/s when erupting
    "average_thermal_power_kdtu_s": float,    # kDTU/s lifetime average
    "thermal_per_eruption_kdtu": float,       # Total kDTU per eruption
}
```

**Calculations:**

```python
# Rates
emission_rate = config['scaledRate']
avg_active = emission_rate * eruption_percent
avg_lifetime = emission_rate * eruption_percent * active_percent

# Eruption cycle
eruption_duration = iteration_length * iteration_percent
idle_duration = iteration_length * (1 - iteration_percent)
eruption_uptime = iteration_percent * 100

# Dormancy cycle
active_duration = year_length * year_percent
dormant_duration = year_length * (1 - year_percent)
active_uptime = year_percent * 100

# Overall
overall_uptime = iteration_percent * year_percent * 100

# Production
kg_per_eruption = emission_rate * eruption_duration
kg_per_cycle = avg_active * iteration_length
kg_per_active = avg_active * active_duration

# Storage (to maintain consumption at average rate)
storage_idle = avg_active * idle_duration
storage_dormancy = avg_lifetime * dormant_duration
recommended = max(storage_idle, storage_dormancy)

# Thermal (if element available)
# DTU = mass × specific_heat × temperature
specific_heat = element_data['specificHeatCapacity']
temp_kelvin = temperature  # from behavior
peak_thermal = emission_rate * specific_heat * temp_kelvin / 1000  # kDTU/s
avg_thermal = avg_lifetime * specific_heat * temp_kelvin / 1000
thermal_per_eruption = kg_per_eruption * specific_heat * temp_kelvin / 1000
```

### Element Data Loading

The `element_loader.py` module loads element properties from ONI game files.

**Search Paths:**
1. `~/.local/share/Steam/steamapps/common/OxygenNotIncluded/OxygenNotIncluded_Data/StreamingAssets/elements/`
2. `~/.steam/steam/steamapps/common/OxygenNotIncluded/OxygenNotIncluded_Data/StreamingAssets/elements/`
3. Environment variable `ONI_INSTALL_PATH` if set

**Files to Load:**
- `gas.yaml` - All gas element properties
- `liquid.yaml` - All liquid element properties

**Extracted Properties:**
```python
{
    "element_id": str,              # e.g., "Steam", "Water"
    "state": str,                   # "Gas" or "Liquid"
    "specific_heat_capacity": float,# For thermal calculations
    "max_mass": float,              # Max kg/tile (liquids only)
}
```

**Caching Strategy:**
- Parse YAML files once on first access
- Cache in module-level dictionary
- Provide `get_element_by_id(element_id)` lookup function

**Error Handling:**
- If YAML files not found: Log warning once, return None for lookups
- If element not in YAML: Return None, allow graceful degradation
- If YAML parse error: Log error, continue with empty cache

## Output Formats

### Compact Format

One-line summary per geyser, useful for quick scanning:

```
Cool Steam Vent #1: 2.1 kg/s avg @ (127.5, 147.0) | 58% erupting, 72% active | 136.9°C Steam
Cool Steam Vent #2: 1.8 kg/s avg @ (89.3, 201.5) | 62% erupting, 68% active | 142.3°C Steam
Natural Gas Geyser #1: 0.3 kg/s avg @ (156.0, 178.0) | 45% erupting, 80% active | 150.0°C Natural Gas
```

**Format:** `{name} #{num}: {avg_kg_s} kg/s avg @ {position} | {eruption%}% erupting, {active%}% active | {temp}°C {element}`

### Detailed Format (Default)

Full breakdown with all planning information:

```
=== Cool Steam Vent #1 ===
Position:         (127.5, 147.0)
Output Element:   Steam (Gas)
Output Temp:      136.9°C

Output Rates:
  Average (lifetime):        2.1 kg/s  (accounts for all downtime)
  Average (when active):     2.9 kg/s  (during active period only)
  Peak (when erupting):      5.4 kg/s  (maximum output rate)

Thermal Output:
  Peak thermal power:          11.2 kDTU/s  (when erupting)
  Average thermal power:        4.3 kDTU/s  (lifetime average)
  Total heat per eruption:  2,615.0 kDTU    (over 233.4s)

Eruption Cycle (short-term):
  Erupting:      233.4s  (0.4 cycles)  → Produces   1.3 t @   2,615 kDTU
  Idle:          167.7s  (0.3 cycles)  → Produces   0.0 kg
  Total cycle:   401.1s  (0.7 cycles)
  Uptime:         58.2%

  Storage for idle period: 0.5 t
    - 1 Gas Reservoir (1,000 kg each)

Dormancy Cycle (long-term):
  Active:        98.2 cycles  ( 58,896.1s)  → Produces 170.8 t @ 353,400 kDTU
  Dormant:       38.2 cycles  ( 22,903.9s)  → Produces   0.0 kg
  Total cycle:  136.3 cycles  ( 81,800.0s)
  Uptime:        72.0%

  Storage for dormancy: 48.1 t
    - 48 Gas Reservoirs (1,000 kg each)

Overall Uptime: 41.9% (58.2% erupting × 72.0% active)

Recommended minimum storage: 48.1 t (dormancy buffer dominates)
```

### Alignment Rules

**For detailed format:**
1. **Section headers** - Left-aligned with proper spacing
2. **Numeric values** - Right-aligned within each section
3. **Units** - Immediately follow numbers (no space before units)
4. **Parentheses** - Opening parentheses align vertically within sections
5. **Durations:**
   - Short (< 1 cycle): `233.4s (0.4 cycles)`
   - Long (≥ 1 cycle): `98.2 cycles (58,896.1s)`
6. **Storage amounts:**
   - Use tons (t) for values ≥ 1000 kg: `48.1 t` not `48,100 kg`
   - Use kg for values < 1000 kg: `486 kg`
7. **Temperature:**
   - Celsius only: `136.9°C` (convert from Kelvin internally)

**Reservoir Capacities (hardcoded):**
- Gas Reservoirs: 1,000 kg each
- Liquid Reservoirs: 5,000 kg each

**Tile Storage:**
- **Gases:** Don't show tile capacity (infinite in theory)
- **Liquids:** Show tile capacity using `maxMass` from element YAML

**Example gas storage:**
```
Storage for dormancy: 48.1 t
  - 48 Gas Reservoirs (1,000 kg each)
```

**Example liquid storage:**
```
Storage for dormancy: 48.1 t
  - 10 Liquid Reservoirs (5,000 kg each)
  - 48 tiles @ 1,000 kg/tile max
```

## CLI Interface

### Command-Line Flags

```bash
geyser_info.py SAVE_PATH [OPTIONS]

Required:
  SAVE_PATH              Path to ONI save file

Optional:
  --format FORMAT        Output format: compact | detailed (default: detailed)
  --debug               Show raw configuration data in addition to formatted output
  --skip-vents          Filter out vents, show only actual geysers
  --list-prefabs        List all geyser prefab types and exit
```

### Usage Examples

```bash
# Default: detailed view of all geysers
python geyser_info.py save.sav

# Compact one-line summaries
python geyser_info.py save.sav --format compact

# Skip vents, show only actual geysers in compact format
python geyser_info.py save.sav --format compact --skip-vents

# Show raw debug data alongside detailed output
python geyser_info.py save.sav --debug

# List all geyser prefab types in the save
python geyser_info.py save.sav --list-prefabs
```

## Error Handling and Edge Cases

### Missing Data Handling

**Geyser not analyzed:**
```
=== Cool Steam Vent #1 ===
Position: (127.5, 147.0)
Status:   Not analyzed yet (requires Field Research skill)
```

**Element type unknown:**
```
=== Unknown Geyser #1 ===
Position:       (127.5, 147.0)
Output Element: Unknown
[... rest of output without thermal calculations ...]
```

**YAML files not found:**
- Show warning message once on stderr
- Continue with degraded functionality (no thermal calculations)
- Storage calculations still work (use hardcoded reservoir capacities)

### Edge Cases

**Zero output rate:**
```
=== Inactive Geyser #1 ===
Position: (127.5, 147.0)
Status:   Inactive/Disabled (zero output rate)
```

**100% uptime (no dormancy):**
- Skip dormancy section entirely
- Show only eruption cycle
- Recommended storage = idle buffer only

**Vents without "Geyser" behavior:**
```
=== GasVent #1 ===
Position: (91.5, 199.0)
Type:     Manual vent (not a natural geyser)
```

### Display Precision

- **Rates:** 1 decimal place (e.g., `2.1 kg/s`)
- **Durations:** 1 decimal place (e.g., `233.4s`, `98.2 cycles`)
- **Storage amounts:** 1 decimal place (e.g., `48.1 t`)
- **Percentages:** 1 decimal place (e.g., `58.2%`)
- **Temperature:** 1 decimal place (e.g., `136.9°C`)
- **Thermal energy:** 1 decimal place for kDTU, 0 decimals for large amounts

## Implementation Checklist

### Phase 1: Element Loader Module
- [ ] Create `oni_save_parser/element_loader.py`
- [ ] Implement YAML loading with search paths
- [ ] Implement element caching
- [ ] Add `get_element_by_id()` lookup function
- [ ] Add error handling for missing files
- [ ] Write unit tests for element loader

### Phase 2: Geyser Extractor
- [ ] Add `extract_geyser_stats()` to `oni_save_parser/extractors.py`
- [ ] Implement all calculation formulas
- [ ] Integrate element loader for thermal calculations
- [ ] Handle edge cases (missing data, zero output, etc.)
- [ ] Write unit tests for extractor

### Phase 3: Geyser Formatters
- [ ] Add `format_geyser_compact()` to `oni_save_parser/formatters.py`
- [ ] Add `format_geyser_detailed()` to `oni_save_parser/formatters.py`
- [ ] Implement alignment logic for detailed format
- [ ] Implement duration formatting (seconds/cycles logic)
- [ ] Implement storage formatting (gas vs liquid)
- [ ] Write unit tests for formatters

### Phase 4: Update geyser_info.py
- [ ] Add `--format` argument
- [ ] Update to use `extract_geyser_stats()`
- [ ] Update to use new formatters
- [ ] Move raw data output to `--debug` mode only
- [ ] Test all flag combinations
- [ ] Update example outputs in code comments

### Phase 5: Testing
- [ ] Test on all test save files
- [ ] Verify alignment with various geyser types
- [ ] Verify thermal calculations accuracy
- [ ] Verify storage calculations
- [ ] Test error handling (missing YAML, unknown elements)
- [ ] Test all CLI flags

### Phase 6: Documentation
- [ ] Update README with new geyser_info.py capabilities
- [ ] Add examples of compact and detailed output
- [ ] Document element YAML loading
- [ ] Update docstrings in all modified files

## Testing Strategy

### Unit Tests

**`test_element_loader.py`:**
- Test YAML parsing
- Test caching behavior
- Test element lookup (found/not found)
- Test error handling (missing files, parse errors)

**`test_extractors.py` (extend existing):**
- Test `extract_geyser_stats()` with various configurations
- Test calculation accuracy
- Test edge cases (zero output, 100% uptime, etc.)
- Test thermal calculations with known element data

**`test_formatters.py` (extend existing):**
- Test compact format output
- Test detailed format output
- Test alignment with various number sizes
- Test gas vs liquid storage formatting
- Test duration formatting (short/long periods)

### Integration Tests

**Test with real save files:**
- Early game save (few geysers)
- Mid game save (multiple analyzed geysers)
- Late game save (many geysers, various types)

**Verify outputs:**
- All geysers found and processed
- Calculations match expected values
- Alignment correct across different geyser types
- No crashes with edge cases

## Future Enhancements

**Possible additions (not in scope for this design):**

1. **JSON output format** - For programmatic consumption
2. **Sorting options** - Sort by output rate, type, position, etc.
3. **Filtering by element** - Show only steam vents, only metal volcanoes, etc.
4. **Graph generation** - Visual timeline of active/dormant cycles
5. **Comparison mode** - Compare multiple geysers side-by-side
6. **Export to CSV** - For external analysis tools

## References

- ONI Wiki: https://oxygennotincluded.wiki.gg/wiki/Geyser
- Element YAML location: `OxygenNotIncluded_Data/StreamingAssets/elements/`
- Existing extractor pattern: `oni_save_parser/extractors.py` (duplicant functions)
- Existing formatter pattern: `oni_save_parser/formatters.py` (duplicant functions)
