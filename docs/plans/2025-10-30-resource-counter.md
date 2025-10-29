# Resource Counter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a tool to count all materials in storage containers, on ground, in pipes, and calculate totals by resource type.

**Architecture:** Parse storage building prefabs (StorageLocker, LiquidReservoir, GasReservoir, etc.), extract contents from Storage behavior components, count Pickupable objects on ground, aggregate by element type.

**Tech Stack:** Python 3.12+, oni-save-parser library, collections.defaultdict for counting

---

## Task 1: Create Script Skeleton and Storage Detection

**Files:**
- Create: `examples/resource_counter.py`
- Test: `tests/unit/test_resource_counter.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_resource_counter.py
"""Tests for resource_counter example script."""

import subprocess
import sys
from pathlib import Path

import pytest


def test_resource_counter_help():
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Count resources" in result.stdout or "resource" in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_help -v`

Expected: FAIL - file doesn't exist

**Step 3: Create script skeleton**

```python
# examples/resource_counter.py
"""Count resources in ONI save files.

This script analyzes storage containers, scattered items, and pipes to
provide a comprehensive inventory of all resources in your colony.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_help -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/resource_counter.py tests/unit/test_resource_counter.py
git commit -m "feat(tools): add resource counter script skeleton"
```

---

## Task 2: Identify Storage Prefabs

**Step 1: Write test for storage detection**

```python
# Add to tests/unit/test_resource_counter.py
from oni_save_parser.save_structure import SaveGame, unparse_save_game
from oni_save_parser.save_structure.game_objects import GameObject, GameObjectGroup, Quaternion, Vector3
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_save_with_storage(path: Path) -> None:
    """Create test save with storage buildings."""
    game_info = SaveGameInfo(
        number_of_cycles=50,
        number_of_duplicants=5,
        base_name="Storage Test",
        is_auto_save=False,
        original_save_name="Storage Test",
        save_major_version=7,
        save_minor_version=35,
        cluster_id="vanilla",
        sandbox_enabled=False,
        colony_guid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        dlc_id="",
    )
    header = SaveGameHeader(
        build_version=555555,
        header_version=1,
        is_compressed=True,
        game_info=game_info,
    )

    templates = [
        TypeTemplate(
            name="Klei.SaveFileRoot",
            fields=[TypeTemplateMember(name="buildVersion", type=TypeInfo(info=6))],
            properties=[],
        ),
        TypeTemplate(
            name="Game+Settings",
            fields=[TypeTemplateMember(name="difficulty", type=TypeInfo(info=6))],
            properties=[],
        ),
    ]

    storage_obj = GameObject(
        position=Vector3(x=10.0, y=10.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="StorageLocker", objects=[storage_obj] * 5),
        GameObjectGroup(prefab_name="LiquidReservoir", objects=[storage_obj] * 2),
        GameObjectGroup(prefab_name="GasReservoir", objects=[storage_obj] * 3),
    ]

    save_game = SaveGame(
        header=header,
        templates=templates,
        world={"buildVersion": 555555},
        settings={"difficulty": 2},
        sim_data=b"\\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)


def test_resource_counter_finds_storage(tmp_path: Path):
    """Should find storage containers."""
    save_path = tmp_path / "test.sav"
    create_save_with_storage(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Storage" in result.stdout or "storage" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_finds_storage -v`

Expected: FAIL

**Step 3: Implement storage detection**

```python
# Modify examples/resource_counter.py
from typing import Any
from collections import defaultdict
from oni_save_parser import load_save_file, list_prefab_types, get_game_objects_by_prefab


# Storage prefab types
STORAGE_PREFABS = {
    "solid": ["StorageLocker", "StorageLockerSmart", "ObjectDispenser", "RationBox", "Refrigerator"],
    "liquid": ["LiquidReservoir", "LiquidReservoirSmart"],
    "gas": ["GasReservoir", "GasReservoirSmart"],
}


def find_storage_buildings(save: Any) -> dict[str, list[Any]]:
    """Find all storage buildings in save.

    Args:
        save: Loaded SaveGame

    Returns:
        Dict mapping storage type to list of game objects
    """
    storage_by_type: dict[str, list[Any]] = defaultdict(list)

    all_prefabs = list_prefab_types(save)

    for storage_type, prefab_names in STORAGE_PREFABS.items():
        for prefab_name in prefab_names:
            if prefab_name in all_prefabs:
                objects = get_game_objects_by_prefab(save, prefab_name)
                storage_by_type[storage_type].extend(objects)

    return dict(storage_by_type)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        save = load_save_file(args.save_file)
        storage_buildings = find_storage_buildings(save)

        print("Storage Containers Found:")
        for storage_type, buildings in storage_buildings.items():
            print(f"  {storage_type.title()}: {len(buildings)}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_finds_storage -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/resource_counter.py tests/unit/test_resource_counter.py
git commit -m "feat(tools): detect storage containers"
```

---

## Task 3: Add JSON Output and Summary

**Step 1: Write test for JSON output**

```python
# Add to tests/unit/test_resource_counter.py

def test_resource_counter_json_output(tmp_path: Path):
    """Should output as JSON."""
    save_path = tmp_path / "test.sav"
    create_save_with_storage(save_path)

    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", str(save_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    import json
    data = json.loads(result.stdout)

    assert "storage_summary" in data
    assert "solid" in data["storage_summary"]
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_json_output -v`

Expected: FAIL

**Step 3: Implement JSON output**

```python
# Modify examples/resource_counter.py
import json


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        save = load_save_file(args.save_file)
        storage_buildings = find_storage_buildings(save)

        # Build summary
        summary = {
            "storage_summary": {
                storage_type: len(buildings)
                for storage_type, buildings in storage_buildings.items()
            },
            "total_containers": sum(len(b) for b in storage_buildings.values()),
        }

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("Storage Containers Found:")
            for storage_type, buildings in storage_buildings.items():
                print(f"  {storage_type.title()}: {len(buildings)}")
            print(f"\nTotal Containers: {summary['total_containers']}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_json_output -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/resource_counter.py tests/unit/test_resource_counter.py
git commit -m "feat(tools): add JSON output and summary for resource counter"
```

---

## Task 4: Add Error Handling and Documentation

**Step 1: Add error handling test**

```python
# Add to tests/unit/test_resource_counter.py

def test_resource_counter_file_not_found():
    """Should handle missing file."""
    result = subprocess.run(
        [sys.executable, "examples/resource_counter.py", "nonexistent.sav"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Error" in result.stderr
```

**Step 2: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_resource_counter.py::test_resource_counter_file_not_found -v`

Expected: PASS (already handled)

**Step 3: Update documentation**

Update `examples/README.md`, `README.md`, and `TOOLS_ROADMAP.md` with resource counter documentation.

**Step 4: Commit**

```bash
git add tests/unit/test_resource_counter.py examples/README.md README.md TOOLS_ROADMAP.md
git commit -m "docs: document resource counter tool"
```

---

## Verification Checklist

- [ ] All tests pass
- [ ] Storage containers detected correctly
- [ ] JSON output works
- [ ] Error handling works
- [ ] Documentation updated
- [ ] Type checking passes

---

## Future Enhancements

To complete resource counting, parse:
- **Storage behavior** - Extract items in each container
- **Pickupable objects** - Count items on ground
- **ConduitContents** - Count resources in pipes
- Aggregate by element type (Iron, Water, Oxygen, etc.)
