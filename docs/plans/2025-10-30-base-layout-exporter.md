# Base Layout Exporter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Export coordinates of all tiles and buildings for visualization in external tools.

**Architecture:** Extract position data from all game objects, group by prefab type, export in multiple formats (CSV, JSON, optionally SVG).

**Tech Stack:** Python 3.12+, oni-save-parser library, csv module, json module

---

## Task 1: Create Script and Extract Positions

**Files:**
- Create: `examples/export_layout.py`
- Test: `tests/unit/test_export_layout.py`

**Step 1: Write help test**

```python
def test_export_layout_help():
    """Should display help."""
    result = subprocess.run(
        [sys.executable, "examples/export_layout.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Export" in result.stdout or "layout" in result.stdout.lower()
```

**Step 2: Create skeleton**

```python
import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export base layout from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument("output_file", type=Path, help="Path to output file")
    
    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 3: Commit**

```bash
git add examples/export_layout.py tests/unit/test_export_layout.py
git commit -m "feat(tools): add base layout exporter skeleton"
```

---

## Task 2: Extract All Object Positions

**Step 1: Write test for position extraction**

```python
def test_export_layout_extracts_positions(tmp_path: Path):
    """Should extract object positions."""
    save_path = tmp_path / "test.sav"
    output_path = tmp_path / "layout.json"
    
    # Create save with objects at known positions
    create_save_with_positioned_objects(save_path)
    
    result = subprocess.run(
        [sys.executable, "examples/export_layout.py", str(save_path), str(output_path)],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert output_path.exists()
    
    import json
    with open(output_path) as f:
        data = json.load(f)
    
    assert "objects" in data
    assert len(data["objects"]) > 0
```

**Step 2: Implement position extraction**

```python
import json
from oni_save_parser import load_save_file, list_prefab_types, get_game_objects_by_prefab


def extract_layout(save):
    """Extract positions of all objects.
    
    Returns:
        List of dicts with prefab, x, y, z
    """
    layout = []
    
    prefab_types = list_prefab_types(save)
    
    for prefab in prefab_types:
        objects = get_game_objects_by_prefab(save, prefab)
        
        for obj in objects:
            layout.append({
                "prefab": prefab,
                "x": obj.position.x,
                "y": obj.position.y,
                "z": obj.position.z,
            })
    
    return layout


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export base layout from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument("output_file", type=Path, help="Path to output file")
    
    args = parser.parse_args()
    
    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1
    
    try:
        save = load_save_file(args.save_file)
        layout = extract_layout(save)
        
        # Export as JSON
        output_data = {
            "source": str(args.save_file),
            "object_count": len(layout),
            "objects": layout,
        }
        
        with open(args.output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Exported {len(layout)} objects to {args.output_file}")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 3: Commit**

```bash
git add examples/export_layout.py tests/unit/test_export_layout.py
git commit -m "feat(tools): extract and export object positions"
```

---

## Task 3: Add CSV Format Support

**Step 1: Write test for CSV output**

```python
def test_export_layout_csv_format(tmp_path: Path):
    """Should export as CSV."""
    save_path = tmp_path / "test.sav"
    output_path = tmp_path / "layout.csv"
    
    create_save_with_positioned_objects(save_path)
    
    result = subprocess.run(
        [sys.executable, "examples/export_layout.py", str(save_path), str(output_path), "--format", "csv"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert output_path.exists()
    
    import csv
    with open(output_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) > 0
    assert "prefab" in rows[0]
    assert "x" in rows[0]
```

**Step 2: Implement CSV export**

```python
import csv


def export_csv(layout, output_file):
    """Export layout as CSV."""
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["prefab", "x", "y", "z"])
        writer.writeheader()
        writer.writerows(layout)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export base layout from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument("output_file", type=Path, help="Path to output file")
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    
    args = parser.parse_args()
    
    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1
    
    try:
        save = load_save_file(args.save_file)
        layout = extract_layout(save)
        
        if args.format == "csv":
            export_csv(layout, args.output_file)
        else:
            # JSON export
            output_data = {
                "source": str(args.save_file),
                "object_count": len(layout),
                "objects": layout,
            }
            
            with open(args.output_file, "w") as f:
                json.dump(output_data, f, indent=2)
        
        print(f"Exported {len(layout)} objects to {args.output_file} ({args.format} format)")
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 3: Commit**

```bash
git add examples/export_layout.py tests/unit/test_export_layout.py
git commit -m "feat(tools): add CSV format support for layout export"
```

---

## Task 4: Add Filtering Options

**Step 1: Add filter test**

```python
def test_export_layout_filter_by_prefab(tmp_path: Path):
    """Should filter to specific prefabs."""
    save_path = tmp_path / "test.sav"
    output_path = tmp_path / "layout.json"
    
    create_save_with_positioned_objects(save_path)
    
    result = subprocess.run(
        [sys.executable, "examples/export_layout.py", str(save_path), str(output_path), "--filter", "Tile"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    
    import json
    with open(output_path) as f:
        data = json.load(f)
    
    # All objects should be Tile prefab
    for obj in data["objects"]:
        assert obj["prefab"] == "Tile"
```

**Step 2: Implement filtering**

```python
def extract_layout(save, filter_prefab=None):
    """Extract positions of objects.
    
    Args:
        save: Loaded SaveGame
        filter_prefab: Optional prefab name to filter to
    
    Returns:
        List of dicts with prefab, x, y, z
    """
    layout = []
    
    if filter_prefab:
        prefab_types = [filter_prefab]
    else:
        prefab_types = list_prefab_types(save)
    
    for prefab in prefab_types:
        objects = get_game_objects_by_prefab(save, prefab)
        
        for obj in objects:
            layout.append({
                "prefab": prefab,
                "x": obj.position.x,
                "y": obj.position.y,
                "z": obj.position.z,
            })
    
    return layout


# In main(), add:
parser.add_argument(
    "--filter",
    type=str,
    help="Filter to specific prefab type",
)

# Pass filter to extract_layout:
layout = extract_layout(save, filter_prefab=args.filter)
```

**Step 3: Commit**

```bash
git add examples/export_layout.py tests/unit/test_export_layout.py
git commit -m "feat(tools): add prefab filtering for layout export"
```

---

## Task 5: Documentation and Testing

- Add error handling tests
- Update examples/README.md
- Update main README.md
- Update TOOLS_ROADMAP.md
- Verify all tests pass

```bash
git add tests/unit/test_export_layout.py examples/README.md README.md TOOLS_ROADMAP.md
git commit -m "docs: document base layout exporter tool"
```

---

## Verification Checklist

- [ ] JSON export works
- [ ] CSV export works
- [ ] Prefab filtering works
- [ ] Error handling for missing files
- [ ] Documentation complete
- [ ] All tests pass

---

## Future Enhancements

- **SVG output** - Generate visual map
- **ASCII art output** - Text-based visualization
- **Bounds detection** - Calculate min/max coordinates
- **Grid snapping** - Round positions to tile grid
- **Layer separation** - Separate by Z coordinate
- **Category filtering** - Filter by building types (power, oxygen, etc.)
