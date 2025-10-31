# ONI Test Save Files

This directory contains a curated set of Oxygen Not Included save files for testing the parser across different game stages and colony sizes.

## Test Files Overview

| File | Cycles | Duplicants | Size | Purpose |
|------|--------|------------|------|---------|
| `01-early-game-cycle-010.sav` | 10 | 5 | 0.8 MB | **Fast baseline test** - Early game colony, quick to load |
| `02-mid-game-cycle-148.sav` | 148 | 22 | 2.2 MB | **Mid-game test** - Established colony with moderate complexity |
| `03-late-game-cycle-1160.sav` | 1,160 | 31 | 12.5 MB | **Late-game test** - Large colony with advanced systems |
| `04-advanced-cycle-1434.sav` | 1,434 | 1 | 29.2 MB | **Advanced colony** - Long-running game with complex infrastructure |
| `05-most-dupes-59-cycle-1423.sav` | 1,423 | **59** | 29.3 MB | **Population stress test** - Maximum duplicant count |
| `06-maximum-cycle-4770.sav` | **4,770** | 16 | 38.2 MB | **Maximum stress test** - Longest gameplay, largest file |

## Usage

### Quick Test (Fast)
```bash
python examples/resource_counter.py test_saves/01-early-game-cycle-010.sav
```

### Comprehensive Test (All Files)
```bash
for save in test_saves/*.sav; do
    echo "Testing $save..."
    python examples/resource_counter.py "$save" --list-elements
done
```

### Performance Benchmarking
```bash
time python examples/resource_counter.py test_saves/06-maximum-cycle-4770.sav
```

## File Details

### 01-early-game-cycle-010.sav
- **Colony:** Coolio Creatures
- **Original:** `Coolio Creatures - 11.sav`
- **Characteristics:** Fresh colony, minimal infrastructure, ideal for quick iteration testing
- **Use Case:** Regression tests, basic functionality verification

### 02-mid-game-cycle-148.sav
- **Colony:** The Doomed Laboratory
- **Original:** `The Doomed Laboratory - Coal.sav`
- **Characteristics:** Established base with power, food, and water systems
- **Use Case:** Feature testing, moderate complexity scenarios

### 03-late-game-cycle-1160.sav
- **Colony:** Impenetrable Spacerock
- **Original:** `maybe broken 6.sav`
- **Characteristics:** Advanced technology, space exploration, complex automation
- **Use Case:** Late-game feature testing, medium stress test

### 04-advanced-cycle-1434.sav
- **Colony:** Grimy Dump
- **Original:** `1435 - tear.sav`
- **Characteristics:** Extensive infrastructure, 1400+ cycles of gameplay
- **Use Case:** Long-term colony testing, data integrity checks
- **Note:** Already verified working with resource_counter (547 prefab types found)

### 05-most-dupes-59-cycle-1423.sav
- **Colony:** Grimy Dump
- **Original:** `1423 - tear.sav`
- **Characteristics:** **59 duplicants** (maximum population), extensive storage systems
- **Use Case:** Duplicant inventory testing, population stress testing
- **Note:** Best for testing duplicant-related features

### 06-maximum-cycle-4770.sav
- **Colony:** Coolio Creatures
- **Original:** `4771 - pipes.sav`
- **Characteristics:** **4,770 cycles**, most advanced colony, 38.2 MB file
- **Use Case:** Maximum stress testing, performance benchmarking, edge case discovery
- **Note:** If parser works on this, it works on everything!

## Source Statistics

These files were selected from a comprehensive analysis of **2,600+ save files** across 87 colony directories:

### Top Directories by Save Count
| Directory | Save Files | Total Size |
|-----------|-----------|------------|
| Coolio Creatures | 913 | 18.4 GB |
| Coolio Creatures - Copy | 879 | 17.1 GB |
| Grimy Dump | 484 | 6.6 GB |
| Impenetrable Spacerock | 232 | 1.1 GB |
| The Doomed Laboratory | 66 | 100 MB |

### Cycle Distribution
- **0-100 cycles:** ~85 saves (early game)
- **100-500 cycles:** ~30 saves (mid game)
- **500-1500 cycles:** ~520 saves (late game)
- **1500+ cycles:** ~1965 saves (advanced/long-term)
- **Maximum:** 4,770 cycles

## Testing Recommendations

### For Development
1. Start with `01-early-game-cycle-010.sav` for fast iteration
2. Verify features on `02-mid-game-cycle-148.sav`
3. Test edge cases on `06-maximum-cycle-4770.sav`

### For CI/CD
1. Quick test: `01-early-game-cycle-010.sav` only
2. Standard test: `01`, `02`, `03` (covers small/medium/large)
3. Full test: All 6 files (performance permitting)

### For Performance Testing
```bash
# Measure load time
time python -c "from oni_save_parser import load_save_file; load_save_file('test_saves/06-maximum-cycle-4770.sav')"

# Measure resource counting
time python examples/resource_counter.py test_saves/06-maximum-cycle-4770.sav --list-elements
```

### For Feature Verification
- **Storage parsing:** Use `05-most-dupes-59-cycle-1423.sav` (extensive storage usage)
- **Duplicant inventory:** Use `05-most-dupes-59-cycle-1423.sav` (59 duplicants)
- **Element variety:** Use `04-advanced-cycle-1434.sav` (547 unique prefab types)
- **Large-scale systems:** Use `06-maximum-cycle-4770.sav` (complex late-game)

## File Size Considerations

Total size of all test files: **112.2 MB**

If storage is a concern, prioritize:
- **Essential:** `01`, `02`, `04` (32.2 MB) - covers small/medium/large
- **Recommended:** Add `05` (61.5 MB) - includes population testing
- **Complete:** All 6 files (112.2 MB) - full test coverage

## Notes

- All files are from real gameplay (not generated/modified)
- Files represent stable save points (not mid-crash or corrupted)
- Colony names and save descriptions preserved from original files
- Files selected to maximize testing coverage across game stages
- Original file paths documented for traceability

## Source Location

Original files located at:
```
~/.config/unity3d/Klei/Oxygen Not Included/cloud_save_files/76561198007417251/
```

Analysis performed: 2025-10-31
