# Example Tools Roadmap

This document tracks the development status of example tools for the ONI Save Parser.

## Status Legend
- ✅ **Complete** - Tool is implemented and tested
- 🚧 **In Progress** - Currently being developed
- 📋 **Planned** - Approved for development
- ⏸️ **On Hold** - Not currently planned
- ❌ **Rejected** - Will not be developed

---

## Completed Tools

### ✅ Geyser Information Tool
**File**: `examples/geyser_info.py`
**Status**: Complete
**Description**: Extract and display geyser data including type, state, emission rates, and dormancy cycles
**Features**:
- List all geyser prefab types
- Display geyser positions and states
- Filter by specific geyser type
- JSON output support
- 7 tests, 100% coverage

**Usage**:
```bash
python examples/geyser_info.py MySave.sav --list-prefabs
python examples/geyser_info.py MySave.sav --json
```

---

## Planned Tools (Priority Order)

### 📋 1. Duplicant Analyzer
**File**: `examples/duplicant_info.py`
**Priority**: High
**Status**: Planned
**Description**: Analyze duplicant data including name, traits, skills, stress, health, location, and current task

**Planned Features**:
- List all duplicants with basic info
- Show detailed traits and skills
- Display stress levels and morale
- Show health status and conditions
- Display current location
- Show current task/activity
- Filter by trait, skill, or status
- JSON output support

**Behavior Components to Parse**:
- `MinionIdentity` - Name and personality
- `AttributeLevels` - Skills and attributes
- `Traits` - Duplicant traits
- `Health` - Health status
- `MinionModifiers` - Active effects
- `ChoreConsumer` - Current task

**Estimated Complexity**: Medium

---

### 📋 2. Resource Counter
**File**: `examples/resource_counter.py`
**Priority**: High
**Status**: Planned
**Description**: Count all materials in storage containers, on ground, and in pipes

**Planned Features**:
- Count resources in solid storage
- Count liquids in tanks
- Count gases in reservoirs
- Count scattered items on ground
- Count resources in pipes/conveyors
- Group by material type
- Show total mass per resource
- Filter by storage type or material
- JSON output support

**Prefab Types to Analyze**:
- `StorageLocker`, `LiquidReservoir`, `GasReservoir`
- `RationBox`, `RefrigeratorBox`
- `Pickupable` (items on ground)
- `ConduitContents` (in pipes)

**Estimated Complexity**: High (requires parsing storage behavior data)

---

### 📋 3. Power Grid Analyzer
**File**: `examples/power_info.py`
**Priority**: High
**Status**: Planned
**Description**: Analyze power generation and consumption across the colony

**Planned Features**:
- List all generators (type, fuel, output wattage)
- Show battery status (charge level, capacity)
- List major power consumers
- Calculate total generation vs consumption
- Show power grid circuits
- Identify power bottlenecks
- Display fuel reserves for generators
- JSON output support

**Prefab Types to Analyze**:
- Generators: `Generator`, `HydroelectricGenerator`, `SteamTurbine2`, `SolarPanel`, etc.
- Batteries: `Battery`, `BatteryMedium`, `BatterySmart`
- Consumers: All powered buildings

**Behavior Components to Parse**:
- `Generator` - Power generation
- `Battery` - Energy storage
- `EnergyConsumer` - Power consumption
- `CircuitManager` - Power grid circuits

**Estimated Complexity**: High (complex behavior data)

---

### 📋 4. Colony Statistics Dashboard
**File**: `examples/colony_stats.py`
**Priority**: High
**Status**: Planned
**Description**: Quick overview of entire colony health and status

**Planned Features**:
- Duplicant count and average stats
- Food supply (calories available)
- Oxygen production rate
- Power status (production/consumption)
- Average morale and stress
- Colony age (cycles)
- Key resource counts
- Building counts by type
- Nice formatted dashboard output
- JSON output support

**Implementation**: Aggregates data from other analyzers

**Estimated Complexity**: Medium (combines multiple analyses)

---

### 📋 5. Critter/Plant Tracker
**File**: `examples/ranch_farm_info.py`
**Priority**: Medium
**Status**: Planned
**Description**: Track ranched critters and farmed plants

**Planned Features**:
- Count critters by species
- Show critter age and status (baby, adult, old)
- Count plants by species
- Show plant growth stage
- Show domestication status
- Display location of ranches/farms
- Calculate reproduction rates
- JSON output support

**Prefab Types to Analyze**:
- Critters: `Hatch`, `Pacu`, `Drecko`, `Pokeshell`, etc.
- Plants: `BasicForagePlant`, `SwampLily`, `PrickleFlower`, etc.

**Behavior Components to Parse**:
- `CreatureBrain` - Critter AI state
- `Age` - Critter age
- `Growing` - Plant growth stage
- `WiltCondition` - Plant health

**Estimated Complexity**: Medium

---

### 📋 6. Save File Differ
**File**: `examples/save_diff.py`
**Priority**: Medium
**Status**: Planned
**Description**: Compare two saves to show what changed between cycles

**Planned Features**:
- Compare two save files
- Show buildings built/destroyed
- Show resources gained/lost
- Show duplicants added/removed
- Show tech researched
- Show geysers discovered
- Diff output format
- JSON output support

**Implementation**: Load two saves and compare game objects

**Estimated Complexity**: High (complex comparison logic)

---

### 📋 7. Base Layout Exporter
**File**: `examples/export_layout.py`
**Priority**: Low
**Status**: Planned
**Description**: Export coordinates of all tiles and buildings for visualization

**Planned Features**:
- Export all tile positions
- Export all building positions with type
- Output in multiple formats (CSV, JSON, SVG)
- Optional: Generate ASCII art map
- Optional: Generate image visualization

**Use Cases**:
- Import into external visualization tools
- Create base maps
- Share base layouts

**Estimated Complexity**: Medium (format conversion)

---

## Not Planned (Skipped)

### ⏸️ Storage Contents Viewer
**Reason**: Covered by Resource Counter
**Description**: View contents of individual storage containers

### ⏸️ Building Counter
**Reason**: Lower priority - covered by Colony Dashboard
**Description**: Count buildings by type

### ⏸️ Food Supply Analyzer
**Reason**: Lower priority - subset of Resource Counter
**Description**: Track food supplies

### ⏸️ Temperature Mapper
**Reason**: Requires temperature grid data (not yet parsed)
**Description**: Map hot/cold spots

### ⏸️ Automation Circuit Tracer
**Reason**: Complex, niche use case
**Description**: Trace automation wires

### ⏸️ Plumbing/Gas Analyzer
**Reason**: Complex, lower priority
**Description**: Analyze pipe networks

---

## Development Notes

### Implementation Priority
1. **Duplicant Analyzer** - Most useful, demonstrates behavior parsing
2. **Resource Counter** - High utility, moderate complexity
3. **Colony Statistics Dashboard** - Good overview tool
4. **Power Grid Analyzer** - Complex but very useful
5. **Critter/Plant Tracker** - Good for ranchers
6. **Save File Differ** - Unique tool, interesting tech
7. **Base Layout Exporter** - Nice to have, lower priority

### Testing Requirements
All tools should include:
- Help message test
- Basic functionality test
- JSON output test
- Error handling test
- Example with test save file

### Documentation Requirements
- Add to `examples/README.md`
- Include usage examples in main README
- Document required behavior components

---

## Progress Tracking

| Tool | Status | Tests | Coverage | Priority |
|------|--------|-------|----------|----------|
| Geyser Info | ✅ Complete | 7 | 100% | - |
| Duplicant Analyzer | 📋 Planned | - | - | High |
| Resource Counter | 📋 Planned | - | - | High |
| Power Grid Analyzer | 📋 Planned | - | - | High |
| Colony Dashboard | 📋 Planned | - | - | High |
| Critter/Plant Tracker | 📋 Planned | - | - | Medium |
| Save File Differ | 📋 Planned | - | - | Medium |
| Base Layout Exporter | 📋 Planned | - | - | Low |

---

## Future Ideas

Tools that might be added in the future:
- **Stress Monitor** - Track stress sources and warnings
- **Decor Mapper** - Show decor values across base
- **Research Tree Viewer** - Show completed/available research
- **Rocket Mission Tracker** - Track rocket missions and cargo
- **Disease Tracker** - Monitor germ spread
- **Job Assignment Optimizer** - Suggest duplicant job assignments

---

Last Updated: 2025-10-30
