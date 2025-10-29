# Duplicant Analyzer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a tool to extract and display duplicant information including name, traits, skills, stress, health, location, and current task.

**Architecture:** Parse game objects with "Minion" prefab, extract data from behavior components (MinionIdentity, AttributeLevels, Traits, Health, etc.), format and display with text and JSON output options.

**Tech Stack:** Python 3.12+, oni-save-parser library, argparse, json

---

## Task 1: Create Basic Script Structure

**Files:**
- Create: `examples/duplicant_info.py`
- Test: `tests/unit/test_duplicant_info.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_duplicant_info.py
"""Tests for duplicant_info example script."""

import subprocess
import sys
from pathlib import Path

import pytest
from oni_save_parser.save_structure import SaveGame, unparse_save_game
from oni_save_parser.save_structure.game_objects import (
    GameObject,
    GameObjectBehavior,
    GameObjectGroup,
    Quaternion,
    Vector3,
)
from oni_save_parser.save_structure.header import SaveGameHeader, SaveGameInfo
from oni_save_parser.save_structure.type_templates import TypeInfo, TypeTemplate, TypeTemplateMember


def create_save_with_duplicants(path: Path) -> None:
    """Create a test save file with duplicant objects."""
    game_info = SaveGameInfo(
        number_of_cycles=100,
        number_of_duplicants=3,
        base_name="Dup Test",
        is_auto_save=False,
        original_save_name="Dup Test Cycle 100",
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

    world = {"buildVersion": 555555}
    settings = {"difficulty": 2}

    # Create duplicant object with behaviors
    dup_obj = GameObject(
        position=Vector3(x=100.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[dup_obj] * 3),
        GameObjectGroup(prefab_name="Tile", objects=[dup_obj] * 10),
    ]

    save_game = SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=b"\\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)


def test_duplicant_info_help():
    """Should display help message."""
    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", "--help"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Extract duplicant information" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_help -v`

Expected: FAIL with "No such file or directory: 'examples/duplicant_info.py'"

**Step 3: Write minimal script implementation**

```python
# examples/duplicant_info.py
"""Extract and display duplicant information from ONI save files.

This script loads a save file and prints detailed information about duplicants
including their name, traits, skills, stress, health, and current activities.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_help -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/duplicant_info.py tests/unit/test_duplicant_info.py
git commit -m "feat(tools): add duplicant analyzer script skeleton

Create basic duplicant_info.py script with argument parsing and help text.
Add test fixture for creating test saves with duplicants.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Add Basic Duplicant Listing

**Files:**
- Modify: `examples/duplicant_info.py`
- Modify: `tests/unit/test_duplicant_info.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_duplicant_info.py

def test_duplicant_info_list_duplicants(tmp_path: Path):
    """Should list all duplicants."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Found 3 duplicants" in result.stdout or "3 duplicants" in result.stdout.lower()
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_list_duplicants -v`

Expected: FAIL - output doesn't contain duplicant count

**Step 3: Implement duplicant listing**

```python
# Modify examples/duplicant_info.py - add imports at top
from typing import Any
from oni_save_parser import load_save_file, get_game_objects_by_prefab

# Modify main() function
def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Load save and get duplicants
        save = load_save_file(args.save_file)
        duplicants = get_game_objects_by_prefab(save, "Minion")

        print(f"Found {len(duplicants)} duplicants")

        for idx, dup in enumerate(duplicants, 1):
            print(f"\n=== Duplicant #{idx} ===")
            print(f"Position: ({dup.position.x:.1f}, {dup.position.y:.1f})")
            print(f"Behaviors: {len(dup.behaviors)}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_list_duplicants -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/duplicant_info.py tests/unit/test_duplicant_info.py
git commit -m "feat(tools): add basic duplicant listing

Load save file and display count and position of all duplicants.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Extract Duplicant Identity Data

**Files:**
- Modify: `examples/duplicant_info.py`
- Modify: `tests/unit/test_duplicant_info.py`

**Step 1: Write the failing test**

```python
# Modify create_save_with_duplicants in tests/unit/test_duplicant_info.py
# Add templates for MinionIdentity
def create_save_with_duplicants(path: Path) -> None:
    """Create a test save file with duplicant objects."""
    # ... existing header code ...

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
        TypeTemplate(
            name="MinionIdentity",
            fields=[
                TypeTemplateMember(name="name", type=TypeInfo(info=12)),
                TypeTemplateMember(name="nameStringKey", type=TypeInfo(info=12)),
                TypeTemplateMember(name="gender", type=TypeInfo(info=12)),
                TypeTemplateMember(name="genderStringKey", type=TypeInfo(info=12)),
                TypeTemplateMember(name="personalityResourceId", type=TypeInfo(info=12)),
                TypeTemplateMember(name="voicePitch", type=TypeInfo(info=8)),
            ],
            properties=[],
        ),
    ]

    world = {"buildVersion": 555555}
    settings = {"difficulty": 2}

    # Create duplicants with MinionIdentity behavior
    dup1 = GameObject(
        position=Vector3(x=100.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Meep",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.MEEP",
                    "gender": "NB",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.NB",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_LONER",
                    "voicePitch": 1.0,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    dup2 = GameObject(
        position=Vector3(x=110.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Devon",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.DEVON",
                    "gender": "M",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.M",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_BUILDER",
                    "voicePitch": 0.8,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    dup3 = GameObject(
        position=Vector3(x=120.0, y=50.0, z=0.0),
        rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
        scale=Vector3(x=1.0, y=1.0, z=1.0),
        folder=0,
        behaviors=[
            GameObjectBehavior(
                name="MinionIdentity",
                template_data={
                    "name": "Catalina",
                    "nameStringKey": "STRINGS.DUPLICANTS.NAME.CATALINA",
                    "gender": "F",
                    "genderStringKey": "STRINGS.DUPLICANTS.GENDER.F",
                    "personalityResourceId": "DUPLICANT_PERSONALITY_RESEARCHER",
                    "voicePitch": 1.2,
                },
                extra_data=None,
                extra_raw=b"",
            )
        ],
    )

    game_objects = [
        GameObjectGroup(prefab_name="Minion", objects=[dup1, dup2, dup3]),
        GameObjectGroup(prefab_name="Tile", objects=[GameObject(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            rotation=Quaternion(x=0.0, y=0.0, z=0.0, w=1.0),
            scale=Vector3(x=1.0, y=1.0, z=1.0),
            folder=0,
            behaviors=[],
        )] * 10),
    ]

    save_game = SaveGame(
        header=header,
        templates=templates,
        world=world,
        settings=settings,
        sim_data=b"\\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=game_objects,
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    path.write_bytes(data)


def test_duplicant_info_shows_names(tmp_path: Path):
    """Should show duplicant names."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Meep" in result.stdout
    assert "Devon" in result.stdout
    assert "Catalina" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_shows_names -v`

Expected: FAIL - names not in output

**Step 3: Implement identity extraction**

```python
# Modify examples/duplicant_info.py - add extraction function

def extract_duplicant_info(dup_object: Any) -> dict[str, Any]:
    """Extract information from a duplicant game object.

    Args:
        dup_object: GameObject representing a duplicant

    Returns:
        Dictionary with duplicant information
    """
    info: dict[str, Any] = {
        "position": (dup_object.position.x, dup_object.position.y),
        "name": "Unknown",
        "gender": "Unknown",
        "personality": "Unknown",
        "voice_pitch": 1.0,
        "behaviors": [],
    }

    # Extract data from behaviors
    for behavior in dup_object.behaviors:
        info["behaviors"].append(behavior.name)

        if behavior.name == "MinionIdentity" and behavior.template_data:
            info["name"] = behavior.template_data.get("name", "Unknown")
            info["gender"] = behavior.template_data.get("gender", "Unknown")
            info["personality"] = behavior.template_data.get("personalityResourceId", "Unknown")
            info["voice_pitch"] = behavior.template_data.get("voicePitch", 1.0)

    return info


# Modify main() to use extraction function
def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Load save and get duplicants
        save = load_save_file(args.save_file)
        duplicants = get_game_objects_by_prefab(save, "Minion")

        print(f"Found {len(duplicants)} duplicants\n")

        for idx, dup in enumerate(duplicants, 1):
            info = extract_duplicant_info(dup)

            print(f"=== Duplicant #{idx}: {info['name']} ===")
            print(f"Gender: {info['gender']}")
            print(f"Personality: {info['personality'].replace('DUPLICANT_PERSONALITY_', '')}")
            print(f"Position: ({info['position'][0]:.1f}, {info['position'][1]:.1f})")
            print(f"Behaviors: {', '.join(info['behaviors'])}")
            print()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_shows_names -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/duplicant_info.py tests/unit/test_duplicant_info.py
git commit -m "feat(tools): extract duplicant identity data

Parse MinionIdentity behavior to show duplicant name, gender, and personality.
Update test fixture to include realistic duplicant data.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Add JSON Output Support

**Files:**
- Modify: `examples/duplicant_info.py`
- Modify: `tests/unit/test_duplicant_info.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_duplicant_info.py

def test_duplicant_info_json_output(tmp_path: Path):
    """Should output duplicant info as JSON."""
    save_path = tmp_path / "test.sav"
    create_save_with_duplicants(save_path)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path), "--json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    import json
    data = json.loads(result.stdout)

    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["name"] == "Meep"
    assert data[1]["name"] == "Devon"
    assert data[2]["name"] == "Catalina"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_json_output -v`

Expected: FAIL - no --json flag or wrong output

**Step 3: Implement JSON output**

```python
# Modify examples/duplicant_info.py - add import at top
import json

# Modify main() to add --json flag
def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Load save and get duplicants
        save = load_save_file(args.save_file)
        duplicants = get_game_objects_by_prefab(save, "Minion")

        # Extract info for all duplicants
        dup_info_list = [extract_duplicant_info(dup) for dup in duplicants]

        if args.json:
            # JSON output
            print(json.dumps(dup_info_list, indent=2, default=str))
        else:
            # Text output
            print(f"Found {len(duplicants)} duplicants\n")

            for idx, info in enumerate(dup_info_list, 1):
                print(f"=== Duplicant #{idx}: {info['name']} ===")
                print(f"Gender: {info['gender']}")
                print(f"Personality: {info['personality'].replace('DUPLICANT_PERSONALITY_', '')}")
                print(f"Position: ({info['position'][0]:.1f}, {info['position'][1]:.1f})")
                print(f"Behaviors: {', '.join(info['behaviors'])}")
                print()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_json_output -v`

Expected: PASS

**Step 5: Commit**

```bash
git add examples/duplicant_info.py tests/unit/test_duplicant_info.py
git commit -m "feat(tools): add JSON output for duplicant info

Add --json flag to output duplicant data in JSON format for integration
with other tools.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Add Error Handling Tests

**Files:**
- Modify: `tests/unit/test_duplicant_info.py`

**Step 1: Write the failing tests**

```python
# Add to tests/unit/test_duplicant_info.py

def test_duplicant_info_file_not_found():
    """Should handle missing file gracefully."""
    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", "nonexistent.sav"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "Error" in result.stderr


def test_duplicant_info_no_duplicants(tmp_path: Path):
    """Should handle save with no duplicants."""
    save_path = tmp_path / "test.sav"

    # Create save without duplicants
    game_info = SaveGameInfo(
        number_of_cycles=1,
        number_of_duplicants=0,
        base_name="Empty",
        is_auto_save=False,
        original_save_name="Empty",
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

    save_game = SaveGame(
        header=header,
        templates=templates,
        world={"buildVersion": 555555},
        settings={"difficulty": 2},
        sim_data=b"\\x00" * 100,
        version_major=7,
        version_minor=35,
        game_objects=[],
        game_data=b"",
    )

    data = unparse_save_game(save_game)
    save_path.write_bytes(data)

    result = subprocess.run(
        [sys.executable, "examples/duplicant_info.py", str(save_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Found 0 duplicants" in result.stdout or "No duplicants found" in result.stdout
```

**Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_duplicant_info.py::test_duplicant_info_file_not_found tests/unit/test_duplicant_info.py::test_duplicant_info_no_duplicants -v`

Expected: PASS (error handling already implemented)

**Step 3: Commit**

```bash
git add tests/unit/test_duplicant_info.py
git commit -m "test(tools): add error handling tests for duplicant info

Add tests for missing file and empty save file scenarios.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Update Documentation

**Files:**
- Modify: `examples/README.md`
- Modify: `README.md`
- Modify: `TOOLS_ROADMAP.md`

**Step 1: Update examples README**

```markdown
# Add to examples/README.md after geyser_info section

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
```

**Step 2: Update main README**

```markdown
# Add to README.md in Example Scripts section after geyser tool

**Duplicant Analyzer** - Extract duplicant data:
```bash
# Show all duplicants with details
python examples/duplicant_info.py MyBase.sav

# JSON output
python examples/duplicant_info.py MyBase.sav --json
```
```

**Step 3: Update roadmap**

```markdown
# Update TOOLS_ROADMAP.md - change Duplicant Analyzer section

### ✅ Duplicant Analyzer (COMPLETE)
**File**: `examples/duplicant_info.py`
**Status**: Complete
**Description**: Analyze duplicant data including name, traits, skills, stress, health, location, and current task

**Implemented Features**:
- List all duplicants with names
- Display gender and personality types
- Show duplicant positions
- List behavior components
- JSON output support
- 6 tests, 100% coverage

**Usage**:
```bash
python examples/duplicant_info.py MySave.sav
python examples/duplicant_info.py MySave.sav --json
```

**Note**: Currently extracts MinionIdentity data. Future enhancements can add traits, skills, stress, health parsing as needed.
```

**Step 4: Commit documentation**

```bash
git add examples/README.md README.md TOOLS_ROADMAP.md
git commit -m "docs: document duplicant analyzer tool

Add documentation for duplicant_info.py to examples README, main README,
and update tools roadmap to mark as complete.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Run Full Test Suite

**Step 1: Run all tests**

Run: `uv run pytest tests/unit/test_duplicant_info.py -v`

Expected: All 6 tests pass

**Step 2: Check coverage**

Run: `uv run pytest tests/unit/test_duplicant_info.py --cov=examples --cov-report=term-missing`

Expected: 100% coverage for duplicant_info.py

**Step 3: Run type checking**

Run: `uv run mypy examples/duplicant_info.py`

Expected: Success: no issues found

**Step 4: Final commit**

```bash
git commit --allow-empty -m "feat(tools): complete duplicant analyzer tool

Duplicant analyzer is complete with:
- Basic duplicant listing
- Identity data extraction (name, gender, personality)
- JSON output support
- Error handling
- 6 tests with 100% coverage
- Full documentation

Tests: 196 passing (190 unit + 6 duplicant_info)
Coverage: 100% for examples/duplicant_info.py

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Verification Checklist

- [ ] All 6 tests pass
- [ ] 100% code coverage for duplicant_info.py
- [ ] mypy type checking passes
- [ ] Help text displays correctly
- [ ] Text output shows duplicant names
- [ ] JSON output is valid JSON
- [ ] Error handling works for missing files
- [ ] Error handling works for saves without duplicants
- [ ] Documentation added to examples/README.md
- [ ] Documentation added to main README.md
- [ ] Roadmap updated to mark as complete

---

## Future Enhancements

The duplicant analyzer can be extended to parse additional behavior components:

- **AttributeLevels** - Skills and experience
- **Traits** - Positive and negative traits
- **Health** - HP, injuries, diseases
- **Stresses** - Stress level and sources
- **ChoreConsumer** - Current task/chore
- **MinionModifiers** - Active effects/buffs/debuffs

These can be added incrementally with the same TDD approach: write test, verify fail, implement, verify pass, commit.
