# Resource Counter Tool - Design Document

**Date:** 2025-10-31
**Status:** Design Approved
**Tool Name:** `resource_counter.py`

## Overview

The Resource Counter tool provides comprehensive inventory tracking of all resources in an ONI colony. It counts materials in storage containers, loose debris, and duplicant inventories, organizing them by element type with location breakdowns.

## Requirements

### Scope

**Track these resource types:**
- Solid elements (iron, coal, refined metals, minerals, etc.)
- Liquid elements (water, oil, petroleum, etc.)
- Gas elements (oxygen, hydrogen, natural gas, etc.)

**Track resources in these locations:**
- Storage containers (storage lockers, reservoirs, ration boxes, etc.)
- Loose debris on ground (pickupable items not in containers)
- Duplicant inventories (items being carried by duplicants)

**Exclude from tracking:**
- Unmined tiles (world terrain)
- Natural water pools/lakes
- Atmospheric gases (free-floating in environment)
- Pipe contents

### Output Requirements

**ASCII Table Output (Summary):**
- Fixed-width columns: Element | State | Storage (kg) | Debris (kg) | Duplicants (kg) | Total (kg) | Items
- Sorted by total mass (descending)
- Summary row showing grand totals
- Clean, readable formatting

**JSON Output (Comprehensive):**
- Summary totals by location type
- Detailed storage container information (ID, position, prefab type, mass per container)
- Duplicant carrier details (name, ID, mass carried)
- Debris totals only (mass and count, no individual tracking)
- Metadata (save file, cycle count, timestamp)

### Filtering Options

- `--element ELEMENT`: Show only specific element(s)
- `--state STATE`: Filter by state (solid/liquid/gas)
- `--min-mass MASS`: Exclude elements below minimum total mass threshold
- `--list-elements`: List all element types found and exit
- Filters use AND logic (cumulative)

### Metrics

For each element, track:
- **Total mass (kg)** - Primary metric
- **Item count** - Number of discrete items/stacks

## Architecture

### Multi-Pass Design

The tool uses three sequential passes with validation:

**Pass 1: Storage Containers**
1. Find all game objects with `Storage` behavior component
2. For each storage object:
   - Extract position from transform/position data
   - Get prefab type (StorageLocker, LiquidReservoir, etc.)
   - Iterate through stored items in Storage component
   - For each item, extract `PrimaryElement` data (element type, mass)
   - Record: container ID, position, prefab type, element, mass

**Pass 2: Loose Debris**
1. Find all game objects with `Pickupable` component
2. Filter out items currently stored (have storage parent reference)
3. For each pickupable:
   - Extract `PrimaryElement` data (element type, mass)
   - Aggregate by element type (no individual item tracking)
   - Increment count and sum mass

**Pass 3: Duplicant Inventories**
1. Find all game objects with `MinionIdentity` component
2. For each duplicant:
   - Get duplicant name from MinionIdentity
   - Find associated inventory/storage component
   - Extract carried items with `PrimaryElement` data
   - Record: duplicant name, duplicant ID, element, mass

### Data Structures

**Internal aggregation structure:**
```python
resources = {
    "Iron": {
        "element": "Iron",
        "state": "solid",
        "storage": {
            "mass_kg": 1500.0,
            "count": 3,
            "containers": [
                {
                    "id": 12345,
                    "position": {"x": 10, "y": 5},
                    "mass_kg": 800.0,
                    "prefab_type": "StorageLocker"
                },
                # ... more containers
            ]
        },
        "debris": {
            "mass_kg": 45.2,
            "count": 12
        },
        "duplicants": {
            "mass_kg": 10.0,
            "count": 2,
            "carriers": [
                {"name": "Meep", "id": 98765, "mass_kg": 5.0},
                {"name": "Bubbles", "id": 98766, "mass_kg": 5.0}
            ]
        },
        "total": {"mass_kg": 1555.2, "count": 17}
    },
    # ... more elements
}
```

**Key characteristics:**
- Storage: Full detail with container list
- Debris: Summary only (mass + count)
- Duplicants: Full detail with carrier list
- Each element includes state (solid/liquid/gas)

### Element State Detection

Element state (solid/liquid/gas) determined by:
- Element ID/name lookup in ONI element table
- Hardcoded mapping for common elements
- Default to "unknown" if element not recognized

### Processing Flow

1. **Load save file** - Use ONI Save Parser
2. **Execute three passes** - Storage → Debris → Duplicants
3. **Aggregate data** - Build element-grouped resource structure
4. **Apply filters** - Element, state, minimum mass
5. **Format output** - ASCII table or JSON based on flag
6. **Display results** - Print to stdout

## Command-Line Interface

```bash
resource_counter.py <save_file> [options]

Positional Arguments:
  save_file             Path to .sav file

Options:
  --json                Output in JSON format (default: ASCII table)
  --element ELEMENT     Filter to specific element (e.g., --element Iron)
  --state STATE         Filter by state: solid, liquid, or gas
  --min-mass MASS       Only show elements with total mass >= MASS kg
  --list-elements       List all element types found and exit
  -h, --help            Show help message
```

### Usage Examples

```bash
# Basic usage - ASCII table
resource_counter.py colony.sav

# JSON output
resource_counter.py colony.sav --json

# Filter to iron only
resource_counter.py colony.sav --element Iron

# Show only liquids
resource_counter.py colony.sav --state liquid

# Exclude trace amounts (< 10kg)
resource_counter.py colony.sav --min-mass 10

# Combined filters
resource_counter.py colony.sav --state solid --min-mass 100 --json

# List available elements
resource_counter.py colony.sav --list-elements
```

## Error Handling

**Invalid save file:**
- Clear error message: "Error: File not found: {path}"
- Exit code 1

**No resources match filters:**
- Message: "No resources match the specified filters"
- Exit code 0 (not an error)

**Missing components in save data:**
- Skip objects gracefully
- Continue processing remaining objects
- Optionally log warnings (not to stdout)

**Malformed data:**
- Catch exceptions during component extraction
- Skip problematic objects
- Continue processing

## Testing Strategy

Following the patterns established in `geyser_info.py` and `duplicant_info.py`:

### Test Coverage (Target: 100%)

1. **Help message test** - Verify `--help` displays usage
2. **List elements test** - Test `--list-elements` flag
3. **Basic resource counting** - Test fixture with known resources
4. **Storage container extraction** - Various container types
5. **Debris counting** - Loose pickupable items
6. **Duplicant inventory** - Items carried by duplicants
7. **Element filtering** - `--element` flag
8. **State filtering** - `--state` flag (solid/liquid/gas)
9. **Mass filtering** - `--min-mass` threshold
10. **Combined filters** - Multiple filters together
11. **JSON output** - Verify structure matches specification
12. **ASCII table** - Verify formatting and sorting
13. **File not found** - Error handling
14. **Invalid element filter** - Non-existent element name
15. **Empty save** - No resources present

### Test Fixtures

- Create test saves with known resource quantities
- Use existing test infrastructure (SaveGame construction)
- Include edge cases (empty inventories, zero-mass items, etc.)

## Implementation Details

### Code Organization

```
examples/resource_counter.py
├── main()              # Entry point, argument parsing
├── load_and_process()  # Orchestrate all passes
├── find_storage()      # Pass 1: Storage containers
├── find_debris()       # Pass 2: Loose pickupables
├── find_duplicants()   # Pass 3: Duplicant inventories
├── aggregate_resources() # Combine all passes
├── apply_filters()     # Filter logic
├── format_table()      # ASCII output formatting
└── format_json()       # JSON output formatting
```

### Dependencies

- **ONI Save Parser** - Core library (existing dependency)
- **argparse** - Command-line parsing (stdlib)
- **json** - JSON output (stdlib)
- **dataclasses** - Type-safe data structures (stdlib)
- **collections** - defaultdict for aggregation (stdlib)

### Code Style

- Type hints throughout
- Functions kept small (<50 lines)
- Separate concerns (extraction vs formatting)
- Comprehensive docstrings
- Follow existing tool patterns

## Future Enhancements

Potential additions for future versions:

1. **Temperature tracking** - Min/max/average temperature per element
2. **Storage capacity** - Show how full containers are
3. **Pipe contents** - Track resources in pipe networks
4. **Food details** - Separate food tracking with calorie counts
5. **Export formats** - CSV output option
6. **Historical tracking** - Compare resource levels across saves
7. **Alerts** - Warn about low resource levels

## References

- Similar tools: `geyser_info.py`, `duplicant_info.py`
- ONI Save Parser documentation
- Game component reference: Storage, Pickupable, MinionIdentity, PrimaryElement
