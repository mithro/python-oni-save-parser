# Tool Output Improvement Design

**Date:** 2025-10-31
**Status:** Approved
**Primary Use Case:** Colony analysis and optimization for gameplay decisions

## Problem Statement

Current tools (duplicant_info.py, geyser_info.py, basic_usage.py) output internal behavior lists instead of useful gameplay information:

- Behavior lists like "KPrefabID, StateMachineController, MinionModifiers..." are debugging data, not colony analysis data
- Users need skills, traits, health, and operational status - not parser internals
- No way to get machine-readable output for scripting/automation

## Goals

1. Show gameplay-relevant information by default (skills, traits, health, status)
2. Support multiple output formats (compact, detailed, json)
3. Preserve behavior lists behind --debug flag for parser development
4. Create reusable data extraction module for consistency across tools

## Architecture

### Core Components

**1. Data Extraction Module (`oni_save_parser/extractors.py`)**
- Reusable functions to extract game data from behaviors
- Shared across all tools for consistency
- Easier to test and maintain

**2. Output Format System**
- `--format compact` (default): Gameplay essentials only
- `--format detailed`: Full stats with organized sections
- `--format json`: Machine-readable for automation
- `--debug`: Show internal behavior lists

**3. Tool Updates**
- duplicant_info.py: Skills, traits, health, status
- geyser_info.py: Eruption stats, skip vents option
- basic_usage.py: Update Example 3 to demonstrate new API

## Data Extraction Functions

### Duplicant Data (`extractors.py`)

```python
def extract_duplicant_skills(minion_resume_behavior) -> dict:
    """Extract skill levels from MinionResume.

    Returns:
        {
            'granted_skills': List[str],
            'mastery_by_skill': Dict[str, int],
            'role_mastery': Dict[str, int]
        }
    """

def extract_duplicant_traits(traits_behavior) -> List[str]:
    """Extract personality traits from Klei.AI.Traits.

    Returns: ['QuickLearner', 'NightOwl', 'MouthBreather']
    """

def extract_health_status(health_behavior) -> dict:
    """Extract health and status information.

    Returns:
        {
            'state': str,  # Alive, Incapacitated, Dead
            'can_be_incapacitated': bool
        }
    """

def extract_attribute_levels(attribute_levels_behavior) -> dict:
    """Extract current attribute levels (health, stress, etc.)."""

def extract_current_activity(storage_behavior, chore_consumer_behavior) -> dict:
    """Extract what duplicant is currently doing and carrying."""
```

### Geyser Data

```python
def extract_geyser_stats(geyser_behavior) -> dict:
    """Extract eruption cycle and output stats.

    Already implemented in geyser_info.py, extract to module.
    """

def calculate_average_output(geyser_stats) -> float:
    """Calculate average kg/cycle output based on eruption patterns."""
```

## Output Format Specifications

### Compact Mode (Default)

Focus: Essential information for quick colony scanning

```
=== Duplicant: Ashkan ===
Gender: MALE
Skills: Mining +7, Building +5, Farming +2
Traits: Quick Learner, Yokel, Mouth Breather
Health: 85/100  Stress: 12%
Position: (118.5, 191.0)
Current Job: Digging at (120, 195)
```

### Detailed Mode

Focus: Organized sections with full statistics

```
=== Duplicant: Ashkan ===
IDENTITY:
  Name: Ashkan
  Gender: MALE
  Arrival: Cycle 1

SKILLS:
  Mining: Level 7 (850 XP)
  Building: Level 5 (450 XP)
  Farming: Level 2 (120 XP)
  [... all skills with XP]

TRAITS:
  Positive: Quick Learner (+15% XP gain)
  Negative: Mouth Breather (-25 breath efficiency)
  Neutral: Yokel

STATUS:
  Health: 85/100
  Stress: 12%
  Morale: +5
  Location: (118.5, 191.0)
  Current Task: Digging
```

### JSON Mode

Focus: Machine-readable for automation/scripting

```json
{
  "name": "Ashkan",
  "gender": "MALE",
  "arrival_cycle": 1,
  "skills": {
    "Mining": {"level": 7, "xp": 850},
    "Building": {"level": 5, "xp": 450},
    "Farming": {"level": 2, "xp": 120}
  },
  "traits": {
    "positive": ["QuickLearner"],
    "negative": ["MouthBreather"],
    "neutral": ["Yokel"]
  },
  "status": {
    "health": {"current": 85, "max": 100},
    "stress": 12,
    "morale": 5
  },
  "position": [118.5, 191.0],
  "current_task": "Digging"
}
```

### Debug Mode

Show internal behaviors for parser development:

```
=== Duplicant: Ashkan ===
[... normal output ...]

DEBUG - Behaviors:
  KPrefabID, StateMachineController, MinionModifiers, [...]
```

## Tool-Specific Changes

### duplicant_info.py

**Remove:**
- Behavior list output

**Add:**
- `--format {compact,detailed,json}` flag (default: compact)
- `--debug` flag to show behaviors
- Skills extraction and display
- Traits parsing and display
- Health/stress/morale display
- Current activity extraction

**Keep:**
- Name, gender, position (already present)

### geyser_info.py

**Remove:**
- Behavior lists from Gas/Liquid Vents

**Add:**
- `--format {compact,detailed,json}` flag
- `--debug` flag to show behaviors
- `--skip-vents` flag (only show actual geysers, not vents)
- Dormancy countdown for active geysers
- Average output per cycle calculation

**Keep:**
- Geyser configuration display (already good)

### basic_usage.py

**Update Example 3:**
- Use new extractors from module
- Show skills and traits instead of behaviors
- Demonstrate proper API usage pattern

## Implementation Plan

### Phase 1: Create Extractors Module (2 hours)

1. Create `src/oni_save_parser/extractors.py`
2. Implement extraction functions:
   - `extract_duplicant_skills()`
   - `extract_duplicant_traits()`
   - `extract_health_status()`
   - `extract_attribute_levels()`
   - `extract_current_activity()`
3. Add unit tests for each extractor using test saves

### Phase 2: Update duplicant_info.py (1.5 hours)

1. Add argparse flags: `--format`, `--debug`
2. Implement output formatters:
   - `format_compact_duplicant()`
   - `format_detailed_duplicant()`
   - `format_json_duplicant()`
3. Replace behavior output with extracted data
4. Update main() to use new formatters
5. Test on all test saves

### Phase 3: Update geyser_info.py (1 hour)

1. Add argparse flags: `--format`, `--debug`, `--skip-vents`
2. Implement output formatters for geysers
3. Move geyser extraction to extractors module
4. Add average output calculation
5. Filter vents when `--skip-vents` is set

### Phase 4: Update basic_usage.py (0.5 hours)

1. Import from extractors module
2. Update Example 3 duplicant analysis
3. Show skills and traits in output
4. Update comments to reflect new API

### Phase 5: Testing and Documentation (1 hour)

1. Run all tools on test saves
2. Verify output formats
3. Update tool docstrings
4. Update examples in README (if exists)

## Testing Strategy

**Test cases:**
- Each extractor function with test saves
- Each output format (compact/detailed/json)
- Debug mode shows behaviors
- Skip-vents flag works correctly
- All tools work on all 6 test saves

**Validation:**
- Compact mode is readable for quick scanning
- Detailed mode shows complete information
- JSON mode is valid and parseable
- Debug mode shows original behavior lists

## Success Criteria

1. ✓ Default output shows gameplay information, not behaviors
2. ✓ Users can choose output format for their use case
3. ✓ Behavior lists available via --debug for development
4. ✓ Shared extractors ensure consistency across tools
5. ✓ All existing test saves work with updated tools

## Future Enhancements

- Add more extractors as useful data is discovered
- Support filtering (e.g., `--skills Mining` to show only miners)
- Add color output for better readability
- Create analysis tools (e.g., "which duplicants need training?")
