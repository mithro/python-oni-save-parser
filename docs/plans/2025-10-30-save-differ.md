# Save File Differ Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Compare two save files to show what changed between cycles: buildings built/destroyed, resources gained/lost, duplicants added.

**Architecture:** Load two saves, compare game object prefab counts, identify additions/removals, calculate resource deltas, format as diff output.

**Tech Stack:** Python 3.12+, oni-save-parser library, difflib for text formatting

---

## Task 1: Create Script with Two-File Loading

**Files:**
- Create: `examples/save_diff.py`
- Test: `tests/unit/test_save_diff.py`

**Step 1: Write test for loading two files**

```python
def test_save_diff_help():
    """Should display help."""
    result = subprocess.run(
        [sys.executable, "examples/save_diff.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Compare" in result.stdout or "diff" in result.stdout.lower()


def test_save_diff_loads_two_files(tmp_path: Path):
    """Should load and compare two saves."""
    save1_path = tmp_path / "save1.sav"
    save2_path = tmp_path / "save2.sav"
    
    # Create two different saves
    create_test_save(save1_path, cycles=100)
    create_test_save(save2_path, cycles=101)
    
    result = subprocess.run(
        [sys.executable, "examples/save_diff.py", str(save1_path), str(save2_path)],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "Comparing" in result.stdout or "Cycle" in result.stdout
```

**Step 2: Implement two-file loading**

```python
import argparse
import sys
from pathlib import Path
from oni_save_parser import load_save_file, get_colony_info, get_prefab_counts


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare two ONI save files to show changes"
    )
    parser.add_argument("save1", type=Path, help="Path to first .sav file (older)")
    parser.add_argument("save2", type=Path, help="Path to second .sav file (newer)")
    
    args = parser.parse_args()
    
    if not args.save1.exists():
        print(f"Error: File not found: {args.save1}", file=sys.stderr)
        return 1
    
    if not args.save2.exists():
        print(f"Error: File not found: {args.save2}", file=sys.stderr)
        return 1
    
    try:
        save1 = load_save_file(args.save1)
        save2 = load_save_file(args.save2)
        
        info1 = get_colony_info(save1)
        info2 = get_colony_info(save2)
        
        print(f"Comparing saves:")
        print(f"  {args.save1.name}: Cycle {info1['cycle']}")
        print(f"  {args.save2.name}: Cycle {info2['cycle']}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Step 3: Commit**

```bash
git add examples/save_diff.py tests/unit/test_save_diff.py
git commit -m "feat(tools): add save differ script skeleton"
```

---

## Task 2: Compare Prefab Counts

**Step 1: Write test for prefab differences**

```python
def test_save_diff_shows_building_changes(tmp_path: Path):
    """Should show buildings added/removed."""
    save1_path = tmp_path / "save1.sav"
    save2_path = tmp_path / "save2.sav"
    
    # Create save1 with 10 generators
    create_save_with_buildings(save1_path, generator_count=10)
    # Create save2 with 15 generators  
    create_save_with_buildings(save2_path, generator_count=15)
    
    result = subprocess.run(
        [sys.executable, "examples/save_diff.py", str(save1_path), str(save2_path)],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "+5" in result.stdout or "added 5" in result.stdout.lower()
    assert "Generator" in result.stdout
```

**Step 2: Implement prefab comparison**

```python
def compare_prefabs(save1, save2):
    """Compare prefab counts between two saves.
    
    Returns:
        Dict with added, removed, and unchanged counts
    """
    counts1 = get_prefab_counts(save1)
    counts2 = get_prefab_counts(save2)
    
    all_prefabs = set(counts1.keys()) | set(counts2.keys())
    
    added = {}
    removed = {}
    changed = {}
    
    for prefab in sorted(all_prefabs):
        count1 = counts1.get(prefab, 0)
        count2 = counts2.get(prefab, 0)
        
        if count1 == 0 and count2 > 0:
            added[prefab] = count2
        elif count1 > 0 and count2 == 0:
            removed[prefab] = count1
        elif count1 != count2:
            changed[prefab] = (count1, count2)
    
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
    }


def display_diff(save1, save2):
    """Display differences between saves."""
    diff = compare_prefabs(save1, save2)
    
    if diff["added"]:
        print("\n=== Added ===")
        for prefab, count in diff["added"].items():
            print(f"  + {prefab}: {count}")
    
    if diff["removed"]:
        print("\n=== Removed ===")
        for prefab, count in diff["removed"].items():
            print(f"  - {prefab}: {count}")
    
    if diff["changed"]:
        print("\n=== Changed ===")
        for prefab, (old, new) in diff["changed"].items():
            delta = new - old
            sign = "+" if delta > 0 else ""
            print(f"  {prefab}: {old} -> {new} ({sign}{delta})")
```

**Step 3: Update main() to use display_diff**

```python
# In main():
display_diff(save1, save2)
```

**Step 4: Commit**

```bash
git add examples/save_diff.py tests/unit/test_save_diff.py
git commit -m "feat(tools): compare prefab counts between saves"
```

---

## Task 3: Add Colony Metadata Diff

Show changes in:
- Cycle count (should increase)
- Duplicant count
- Colony name (if changed)

**Step 1: Write test**

```python
def test_save_diff_shows_cycle_change(tmp_path: Path):
    """Should show cycle increase."""
    save1_path = tmp_path / "save1.sav"
    save2_path = tmp_path / "save2.sav"
    
    create_test_save(save1_path, cycles=100, duplicants=5)
    create_test_save(save2_path, cycles=105, duplicants=6)
    
    result = subprocess.run(
        [sys.executable, "examples/save_diff.py", str(save1_path), str(save2_path)],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "100" in result.stdout and "105" in result.stdout
    assert "5" in result.stdout and "6" in result.stdout
```

**Step 2: Implement metadata diff**

```python
def display_metadata_diff(info1, info2):
    """Display metadata differences."""
    print("\n=== Colony Changes ===")
    
    if info1["cycle"] != info2["cycle"]:
        delta = info2["cycle"] - info1["cycle"]
        print(f"  Cycles: {info1['cycle']} -> {info2['cycle']} (+{delta})")
    
    if info1["duplicant_count"] != info2["duplicant_count"]:
        delta = info2["duplicant_count"] - info1["duplicant_count"]
        sign = "+" if delta > 0 else ""
        print(f"  Duplicants: {info1['duplicant_count']} -> {info2['duplicant_count']} ({sign}{delta})")
```

**Step 3: Commit**

```bash
git add examples/save_diff.py tests/unit/test_save_diff.py
git commit -m "feat(tools): add colony metadata diff"
```

---

## Task 4: Add JSON Output

**Step 1: Write JSON output test**

```python
def test_save_diff_json_output(tmp_path: Path):
    """Should output diff as JSON."""
    save1_path = tmp_path / "save1.sav"
    save2_path = tmp_path / "save2.sav"
    
    create_test_save(save1_path, cycles=100)
    create_test_save(save2_path, cycles=101)
    
    result = subprocess.run(
        [sys.executable, "examples/save_diff.py", str(save1_path), str(save2_path), "--json"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    
    import json
    data = json.loads(result.stdout)
    
    assert "metadata_diff" in data
    assert "prefab_diff" in data
```

**Step 2: Implement JSON output**

```python
import json


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare two ONI save files to show changes"
    )
    parser.add_argument("save1", type=Path, help="Path to first .sav file (older)")
    parser.add_argument("save2", type=Path, help="Path to second .sav file (newer)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # ... load files ...
    
    try:
        save1 = load_save_file(args.save1)
        save2 = load_save_file(args.save2)
        
        info1 = get_colony_info(save1)
        info2 = get_colony_info(save2)
        
        prefab_diff = compare_prefabs(save1, save2)
        
        if args.json:
            output = {
                "save1": {
                    "file": str(args.save1),
                    "cycle": info1["cycle"],
                    "duplicants": info1["duplicant_count"],
                },
                "save2": {
                    "file": str(args.save2),
                    "cycle": info2["cycle"],
                    "duplicants": info2["duplicant_count"],
                },
                "metadata_diff": {
                    "cycle_delta": info2["cycle"] - info1["cycle"],
                    "duplicant_delta": info2["duplicant_count"] - info1["duplicant_count"],
                },
                "prefab_diff": prefab_diff,
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Comparing saves:")
            print(f"  {args.save1.name}: Cycle {info1['cycle']}")
            print(f"  {args.save2.name}: Cycle {info2['cycle']}")
            
            display_metadata_diff(info1, info2)
            display_diff(save1, save2)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 3: Commit**

```bash
git add examples/save_diff.py tests/unit/test_save_diff.py
git commit -m "feat(tools): add JSON output for save differ"
```

---

## Task 5: Documentation and Error Handling

- Add test for mismatched save versions
- Add test for same file twice
- Update documentation
- Verify all tests pass

```bash
git add tests/unit/test_save_diff.py examples/README.md README.md TOOLS_ROADMAP.md
git commit -m "docs: document save differ tool"
```

---

## Verification Checklist

- [ ] Loads two saves successfully
- [ ] Shows prefab additions/removals/changes
- [ ] Shows metadata diff (cycles, duplicants)
- [ ] JSON output works
- [ ] Error handling for missing files
- [ ] Documentation complete
- [ ] All tests pass

---

## Future Enhancements

- Color-coded diff output (red for removed, green for added)
- Filter by prefab category (buildings, critters, plants)
- Resource mass deltas (requires parsing storage contents)
- Tech research diff (requires parsing research tree)
