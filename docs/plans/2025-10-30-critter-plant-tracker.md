# Critter/Plant Tracker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Track ranched critters and farmed plants, showing counts by species, age, and growth stage.

**Architecture:** Identify critter prefabs (Hatch, Pacu, Drecko, etc.) and plant prefabs (BasicForagePlant, etc.), parse Age and Growing behaviors, display organized by species.

**Tech Stack:** Python 3.12+, oni-save-parser library

---

## Task 1: Create Script and Identify Critters

**Files:**
- Create: `examples/ranch_farm_info.py`
- Test: `tests/unit/test_ranch_farm_info.py`

**Critter Prefabs to Detect:**
```python
CRITTER_PREFABS = [
    "Hatch",
    "HatchHard", 
    "HatchMetal",
    "Pacu",
    "PacuTropical",
    "PacuCleaner",
    "Drecko",
    "DreckoPlastic",
    "LightBug",
    "Mole",
    "Squirrel",
    "Crab",
    "Bee",
    "Divergent",
]
```

Follow TDD pattern:
1. Write help test
2. Create skeleton
3. Write critter detection test
4. Implement critter detection
5. Commit

---

## Task 2: Add Plant Detection

**Plant Prefabs:**
```python
PLANT_PREFABS = [
    "BasicForagePlant",
    "SwampLily",
    "PrickleFlower",
    "Oxyfern",
    "ColdWheat",
    "GasGrass",
    "SeaLettuce",
    "SpiceVine",
    "BeanPlant",
    "WormPlant",
]
```

Test and implement plant detection similar to critters.

---

## Task 3: Count and Categorize

**Step 1: Write test for species counts**

```python
def test_ranch_farm_info_counts_species(tmp_path: Path):
    """Should count critters by species."""
    # Create save with multiple Hatch, Pacu
    # Verify counts in output
```

**Step 2: Implement species counting**

```python
from collections import Counter

def count_by_species(save):
    """Count critters and plants by species."""
    critter_counts = Counter()
    for prefab in CRITTER_PREFABS:
        objects = get_game_objects_by_prefab(save, prefab)
        if objects:
            critter_counts[prefab] = len(objects)
    
    plant_counts = Counter()
    for prefab in PLANT_PREFABS:
        objects = get_game_objects_by_prefab(save, prefab)
        if objects:
            plant_counts[prefab] = len(objects)
    
    return critter_counts, plant_counts
```

---

## Task 4: Add JSON Output and Formatting

Add --json flag, format output nicely:

```
=== Critters ===
Hatch: 12
Pacu: 8

=== Plants ===
Mealwood: 24
Bristle Blossom: 16

Total Critters: 20
Total Plants: 40
```

---

## Task 5: Documentation and Testing

- Error handling tests
- Update documentation
- Verify all tests pass

---

## Future Enhancements

Parse behaviors to show:
- **Age behavior** - Show baby/adult/old
- **Growing behavior** - Show growth stage %
- **WiltCondition behavior** - Show plant health
- **CreatureBrain behavior** - Show tame/wild status
