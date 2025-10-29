# Colony Statistics Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a comprehensive dashboard showing colony health: duplicants, food, oxygen, power, morale, resources.

**Architecture:** Aggregate data from other tools/functions, combine colony metadata with game object analysis, format as nice dashboard with sections.

**Tech Stack:** Python 3.12+, oni-save-parser library, uses get_colony_info, get_prefab_counts

---

## Task 1: Create Dashboard Script Skeleton

**Files:**
- Create: `examples/colony_stats.py`
- Test: `tests/unit/test_colony_stats.py`

Follow TDD pattern:
1. Write help test
2. Create skeleton
3. Commit

---

## Task 2: Add Colony Metadata Section

**Step 1: Write test for metadata**

```python
def test_colony_stats_shows_metadata(tmp_path: Path):
    """Should show colony name, cycle, duplicants."""
    # Create test save
    # Run script
    # Verify output contains colony name, cycle count, duplicant count
```

**Step 2: Implement metadata display**

```python
from oni_save_parser import load_save_file, get_colony_info

def display_metadata(save):
    """Display colony metadata."""
    info = get_colony_info(save)
    print("=== Colony Overview ===")
    print(f"Name: {info['colony_name']}")
    print(f"Cycle: {info['cycle']}")
    print(f"Duplicants: {info['duplicant_count']}")
    print(f"Cluster: {info['cluster_id']}")
```

---

## Task 3: Add Resource Summary

Count key resources using get_prefab_counts:
- StorageLocker count
- Food containers (RationBox, Refrigerator)
- Power generators
- Oxygen diffusers

**Step 1: Write test**

```python
def test_colony_stats_shows_resources(tmp_path: Path):
    """Should show resource summary."""
    # Create save with various buildings
    # Verify counts in output
```

**Step 2: Implement resource summary**

```python
from oni_save_parser import get_prefab_counts

def display_resources(save):
    """Display resource summary."""
    counts = get_prefab_counts(save)
    
    print("\n=== Resources & Buildings ===")
    print(f"Storage Lockers: {counts.get('StorageLocker', 0)}")
    print(f"Food Storage: {counts.get('RationBox', 0) + counts.get('Refrigerator', 0)}")
    print(f"Generators: {counts.get('Generator', 0)}")
    print(f"Oxygen Diffusers: {counts.get('OxygenDiffuser', 0)}")
```

---

## Task 4: Add JSON Output and Formatting

**Step 1: Add JSON output test**

```python
def test_colony_stats_json_output(tmp_path: Path):
    """Should output as JSON."""
    # Test JSON structure
```

**Step 2: Implement JSON output**

```python
import json

def main():
    # ... load save ...
    
    if args.json:
        dashboard_data = {
            "colony": get_colony_info(save),
            "resources": get_prefab_counts(save),
        }
        print(json.dumps(dashboard_data, indent=2))
    else:
        display_metadata(save)
        display_resources(save)
```

---

## Task 5: Documentation

- Update examples/README.md
- Update main README.md  
- Update TOOLS_ROADMAP.md
- Add error handling tests

---

## Verification

- [ ] Metadata displays correctly
- [ ] Resource counts shown
- [ ] JSON output valid
- [ ] All tests pass
- [ ] Documentation complete

---

## Future Enhancements

Add sections for:
- Average duplicant stress/morale (parse from behaviors)
- Food calorie totals (parse storage contents)
- Oxygen production rate (parse OxygenDiffuser behaviors)
- Power net (generation - consumption)
- Water/Gas reserves
