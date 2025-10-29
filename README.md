# ONI Save Parser (Python)

A Python library for parsing and manipulating Oxygen Not Included save files.

[![Tests](https://img.shields.io/badge/tests-156%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-91.79%25-success)](tests/)
[![Type Checking](https://img.shields.io/badge/mypy-passing-success)](src/)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)

## Features

- 🎮 **Complete Save File Support**: Parse all sections of ONI save files (header, templates, world, settings, game objects)
- 🔍 **Type-Safe**: Full type hints with mypy validation
- 📦 **Easy to Use**: Simple high-level API for common tasks
- 🛠️ **CLI Tool**: Command-line interface for quick analysis
- 🔄 **Round-Trip**: Parse and write back with byte-identical results
- 🧪 **Well Tested**: 156 tests with 91.79% coverage
- 📚 **Documented**: Comprehensive docstrings and examples

## Installation

```bash
# Clone the repository
git clone https://github.com/mithro/oni-save-parser.git
cd oni-save-parser/.worktrees/python-parser

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

## Quick Start

### Python API

```python
from oni_save_parser import load_save_file, get_colony_info

# Load a save file
save = load_save_file("MyBase.sav")

# Get colony information
info = get_colony_info(save)
print(f"Colony: {info['colony_name']}")
print(f"Cycle: {info['cycle']}")
print(f"Duplicants: {info['duplicant_count']}")

# Access game objects
from oni_save_parser import get_game_objects_by_prefab

minions = get_game_objects_by_prefab(save, "Minion")
print(f"Found {len(minions)} duplicants")

for minion in minions:
    print(f"Position: ({minion.position.x}, {minion.position.y})")

    # Access behavior data (components)
    for behavior in minion.behaviors:
        if behavior.name == "MinionIdentity":
            print(f"  Name: {behavior.template_data.get('name')}")
```

### Command-Line Interface

```bash
# Display colony information
python -m oni_save_parser info MyBase.sav

# Output as JSON
python -m oni_save_parser info MyBase.sav --json

# List all prefab types
python -m oni_save_parser prefabs MyBase.sav

# Show object counts by prefab
python -m oni_save_parser prefabs MyBase.sav --counts
```

## API Reference

### High-Level Functions

#### `load_save_file(file_path, verify_version=True, allow_minor_mismatch=True)`
Load an ONI save file from disk.

**Parameters:**
- `file_path` (str | Path): Path to the .sav file
- `verify_version` (bool): Whether to verify save version compatibility (default: True)
- `allow_minor_mismatch` (bool): Allow different minor versions (default: True)

**Returns:** `SaveGame` object

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `VersionMismatchError`: If save version is incompatible
- `CorruptionError`: If save data is corrupted

#### `save_to_file(save_game, file_path)`
Write a SaveGame to disk.

**Parameters:**
- `save_game` (SaveGame): SaveGame structure to write
- `file_path` (str | Path): Output path for the .sav file

#### `get_colony_info(save_game)`
Extract colony information from a save game.

**Returns:** Dictionary with keys:
- `colony_name`: Base name
- `cycle`: Current cycle number
- `duplicant_count`: Number of duplicants
- `cluster_id`: World cluster ID
- `dlc_id`: DLC identifier
- `is_auto_save`: Whether this is an auto-save
- `sandbox_enabled`: Whether sandbox mode is enabled
- `save_version`: Save file version string
- `build_version`: Game build version
- `compressed`: Whether save is compressed

#### `get_game_objects_by_prefab(save_game, prefab_name)`
Get all game objects with a specific prefab name.

**Parameters:**
- `save_game` (SaveGame): Parsed SaveGame
- `prefab_name` (str): Prefab name (e.g., "Minion", "Tile", "Door")

**Returns:** List of GameObject instances

#### `list_prefab_types(save_game)`
List all prefab types present in the save file.

**Returns:** List of prefab name strings

#### `get_prefab_counts(save_game)`
Get count of game objects for each prefab type.

**Returns:** Dictionary mapping prefab names to counts

### Core Types

#### `SaveGame`
Complete ONI save game structure with fields:
- `header`: SaveGameHeader
- `templates`: list[TypeTemplate]
- `world`: dict[str, Any] (Klei.SaveFileRoot template data)
- `settings`: dict[str, Any] (Game+Settings template data)
- `sim_data`: bytes (simulation binary data)
- `version_major`: int
- `version_minor`: int
- `game_objects`: list[GameObjectGroup]
- `game_data`: bytes (additional game state)

#### `GameObject`
Game entity with transform and behaviors:
- `position`: Vector3
- `rotation`: Quaternion
- `scale`: Vector3
- `folder`: int (prefab folder ID)
- `behaviors`: list[GameObjectBehavior]

#### `GameObjectBehavior`
Component attached to a game object:
- `name`: str (.NET class name)
- `template_data`: dict[str, Any] | None (parsed fields/properties)
- `extra_data`: Any | None (special behavior data)
- `extra_raw`: bytes (unparsed data)

## Examples

### Modifying Save Files

```python
from oni_save_parser import load_save_file, save_to_file

# Load the save
save = load_save_file("MyBase.sav")

# Modify colony name
save.header.game_info.base_name = "My Awesome Colony"

# Write back
save_to_file(save, "MyBase_modified.sav")
```

### Analyzing Duplicants

```python
from oni_save_parser import load_save_file, get_game_objects_by_prefab

save = load_save_file("MyBase.sav")
minions = get_game_objects_by_prefab(save, "Minion")

for minion in minions:
    for behavior in minion.behaviors:
        if behavior.name == "MinionIdentity":
            name = behavior.template_data.get("name", "Unknown")
            print(f"Duplicant: {name}")

        if behavior.name == "Health":
            hp = behavior.template_data.get("hitpoints", 0)
            max_hp = behavior.template_data.get("maxHitpoints", 100)
            print(f"  Health: {hp}/{max_hp}")
```

### Counting Resources

```python
from oni_save_parser import load_save_file, get_prefab_counts

save = load_save_file("MyBase.sav")
counts = get_prefab_counts(save)

print("Colony Statistics:")
print(f"  Duplicants: {counts.get('Minion', 0)}")
print(f"  Buildings: {sum(v for k, v in counts.items() if 'Door' in k or 'Bed' in k)}")
print(f"  Total Objects: {sum(counts.values())}")
```

## Architecture

The parser is organized into several layers:

1. **Binary Parser Layer** (`parser/`): Low-level binary reading/writing with proper type support
2. **Type System Layer** (`save_structure/type_templates/`): KSerialization type templates (24 type codes)
3. **Save Structure Layer** (`save_structure/`): Header, templates, world, settings, sim data
4. **Game Objects Layer** (`save_structure/game_objects/`): Game entities, behaviors, transforms
5. **High-Level API** (`api.py`): Convenient functions for common tasks
6. **CLI Tool** (`__main__.py`): Command-line interface

### Design Principles

- **Type Safety**: Full type hints with mypy validation
- **Test-Driven**: Comprehensive test coverage (156 tests)
- **Idempotent**: Round-trip parsing produces byte-identical results
- **Error Handling**: Custom exception types with offset tracking
- **Preservation**: Unknown data is kept as raw bytes

## Supported Save Versions

- **Current**: 7.35 (fully tested)
- **Compatible**: 7.x with `allow_minor_mismatch=True`
- **Older versions**: May work but untested

## Development

```bash
# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=src/oni_save_parser --cov-report=term-missing

# Run performance benchmarks
uv run pytest tests/benchmark --benchmark-only

# Type checking
uv run mypy src/oni_save_parser

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/
```

### Performance Benchmarks

The project includes comprehensive performance benchmarks to track performance over time:

- **API operations**: ~400-700ns (colony info, prefab counts)
- **Small saves** (125 objects): ~600μs parse, ~850μs serialize
- **Medium saves** (1,110 objects): ~5.5ms parse, ~3.2ms serialize
- **Large saves** (5,520 objects): ~30ms parse, ~15ms serialize

Run benchmarks with statistics:
```bash
uv run pytest tests/benchmark --benchmark-only --benchmark-columns=min,mean,max,stddev
```

## Project Status

✅ **Complete Core Implementation**
- Phase 1: Foundation Layer (binary parsing)
- Phase 2: Type System (KSerialization)
- Phase 3: Save File Structure (header, templates, world, settings)
- Phase 4: Game Objects (entities, behaviors, transforms)
- Phase 5: High-Level API & CLI

🚧 **Future Enhancements**
- Game data section parsing (currently preserved as raw bytes)
- Special behavior extra data (Storage, Modifiers)
- Performance optimizations for large saves
- Additional CLI commands (extract, modify)
- Web-based save editor

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Ensure all tests pass and mypy is happy
5. Submit a pull request

## License

MIT

## Credits

- Based on the TypeScript [oni-save-parser](https://github.com/robophred/oni-save-parser) by robophred
- Python port by Claude Code with guidance from mithro
- Oxygen Not Included is developed by Klei Entertainment

## Related Projects

- [oni-save-parser](https://github.com/robophred/oni-save-parser) - Original TypeScript implementation
- [ONI-Mods-by-Peter-Han](https://github.com/peterhaneve/ONIMods) - C# mod framework
