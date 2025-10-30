# ONI Save Parser Examples

This directory contains example scripts demonstrating how to use the ONI Save Parser library.

## Available Examples

### basic_usage.py

Comprehensive examples demonstrating all major features of the library:

1. **Loading and inspecting save files** - Basic file I/O operations
2. **Extracting colony information** - Get colony metadata
3. **Working with game objects** - Filter and analyze game entities
4. **Filtering by prefab type** - Find specific object types
5. **Round-trip operations** - Load, modify, and save files

Run it:
```bash
uv run python examples/basic_usage.py path/to/save.sav
```

### geyser_info.py

Extract and display detailed geyser information from save files.

**Features:**
- List all geyser prefab types in a save
- Display geyser positions and states
- Show emission rates and dormancy cycles
- Filter by specific geyser type
- JSON output support

**Usage:**

List all geyser types:
```bash
uv run python examples/geyser_info.py MySave.sav --list-prefabs
```

Show all geysers:
```bash
uv run python examples/geyser_info.py MySave.sav
```

Filter to specific geyser type:
```bash
uv run python examples/geyser_info.py MySave.sav --prefab GeyserGeneric_steam
```

JSON output:
```bash
uv run python examples/geyser_info.py MySave.sav --json
```

### duplicant_info.py

Extract and display detailed duplicant information.

**Features:**
- List all duplicants with names
- Display gender and personality types
- Show duplicant positions
- List behavior components
- JSON output support

**Usage:**

Show all duplicants:
```bash
uv run python examples/duplicant_info.py MySave.sav
```

JSON output:
```bash
uv run python examples/duplicant_info.py MySave.sav --json
```

### colony_scanner.py

Scan directories for ONI save files and display colony status overview.

**Features:**
- Automatically scans default ONI save directory
- Displays table of all colonies with key stats
- Shows colony name, cycle, duplicant count, last modified date
- Supports custom directory scanning
- JSON output for integration with other tools

**Usage:**

Scan default ONI save directory:
```bash
uv run python examples/colony_scanner.py
```

Scan custom directory:
```bash
uv run python examples/colony_scanner.py /path/to/save/directory
```

JSON output:
```bash
uv run python examples/colony_scanner.py --json
```

## Creating Your Own Scripts

Basic template:

```python
from pathlib import Path
from oni_save_parser import load_save_file, get_game_objects_by_prefab

# Load save file
save = load_save_file("path/to/save.sav")

# Get colony info
info = save.header.game_info
print(f"Colony: {info.base_name}")
print(f"Cycle: {info.number_of_cycles}")

# Find specific objects
duplicants = get_game_objects_by_prefab(save, "Minion")
print(f"Found {len(duplicants)} duplicants")

# Access object data
for dup in duplicants:
    print(f"Position: ({dup.position.x}, {dup.position.y})")
    for behavior in dup.behaviors:
        print(f"  Component: {behavior.name}")
```

## Common Use Cases

### Finding Specific Objects

```python
from oni_save_parser import list_prefab_types, get_game_objects_by_prefab

# List all object types in save
prefabs = list_prefab_types(save)
print("Available prefabs:", prefabs)

# Get all oxygen diffusers
diffusers = get_game_objects_by_prefab(save, "OxygenDiffuser")

# Get all power generators
coal_gens = get_game_objects_by_prefab(save, "Generator")
```

### Analyzing Object Properties

```python
# Each GameObject has:
# - position: Vector3(x, y, z)
# - rotation: Quaternion(x, y, z, w)
# - scale: Vector3(x, y, z)
# - folder: int (prefab type index)
# - behaviors: list[GameObjectBehavior]

for obj in objects:
    print(f"Position: {obj.position}")
    for behavior in obj.behaviors:
        print(f"  Behavior: {behavior.name}")
        if behavior.template_data:
            print(f"    Data: {behavior.template_data}")
```

### Counting Objects by Type

```python
from oni_save_parser import get_prefab_counts

counts = get_prefab_counts(save)
for prefab, count in sorted(counts.items()):
    print(f"{prefab}: {count}")
```

### Modifying and Saving

```python
from oni_save_parser import save_to_file

# Load save
save = load_save_file("input.sav")

# Modify data (be careful!)
save.header.game_info.base_name = "Modified Colony"

# Save to new file
save_to_file(save, "output.sav")
```

## Tips

1. **Real save files are large** - Parsing can take several seconds for large colonies
2. **Test on copies** - Always work on copies of your save files
3. **Check versions** - Use `allow_minor_mismatch=True` for flexibility
4. **Explore behaviors** - Most game logic is in behavior components
5. **Use JSON output** - For integration with other tools

## Getting Help

- Check the main [README](../README.md) for API documentation
- Review test files in `tests/` for more examples
- Open an issue on GitHub for questions

## Contributing Examples

We welcome new examples! If you've created a useful script:

1. Add it to this directory
2. Include docstrings and comments
3. Add tests in `tests/unit/test_<your_script>.py`
4. Update this README
5. Submit a pull request
