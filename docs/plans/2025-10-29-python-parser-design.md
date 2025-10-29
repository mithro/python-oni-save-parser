# Python ONI Save Parser - Design Document

**Date:** 2025-10-29
**Status:** Approved
**Author:** Design session with Claude Code

## Overview

This document describes the design for a Python-based library to parse Oxygen Not Included (ONI) save files. The library will be a direct port of the existing TypeScript oni-save-parser library, with comprehensive testing and eventual refactoring to Pythonic idioms.

## Goals

### Primary Use Cases
1. **Read-only analysis** - Extract statistics and generate reports from save files
2. **Save editing** - Modify duplicants, buildings, and resources with full read/write support
3. **Research/experimentation** - Understand the save format and test ideas
4. **Integration** - Provide clean API for use by other Python programs and tools

### Success Criteria
- Idempotent load/save cycles (bit-for-bit preservation of unmodified data)
- 80%+ code coverage with comprehensive test suite
- 100% type checking (mypy strict mode)
- Cross-validation: 100% match with TypeScript parser on test fixtures
- Clean, well-documented API for Python developers

## Design Decisions

### Technology Stack
- **Python Version:** 3.12+ (modern type hints, pattern matching)
- **Build Tool:** uv (fast, modern package management)
- **Testing:** pytest with hypothesis for property-based testing
- **Type Checking:** mypy in strict mode
- **Linting/Formatting:** ruff (fast, modern linter and formatter)
- **CI/CD:** GitHub Actions

### Implementation Strategy
**Test-Driven Incremental Port:**
1. Start with comprehensive test suite (port TypeScript tests + add new ones)
2. Port module-by-module from bottom-up (dependencies first)
3. Validate each module with round-trip tests before moving forward
4. Cross-validate with TypeScript parser at each phase
5. Initial implementation maintains TypeScript structure for easier validation
6. Refactor to Pythonic idioms after core functionality proven

## Architecture

### Project Structure

```
oni-save-parser-python/
├── pyproject.toml          # uv/pip project configuration
├── README.md
├── LICENSE
├── .github/
│   └── workflows/
│       ├── test.yml        # CI pipeline
│       └── publish.yml     # PyPI publishing
├── src/
│   └── oni_save_parser/
│       ├── __init__.py     # Public API
│       ├── parser/         # Binary read/write primitives
│       │   ├── __init__.py
│       │   ├── parse.py    # Read operations (BinaryParser)
│       │   ├── unparse.py  # Write operations (BinaryWriter)
│       │   └── errors.py   # ParseError and exceptions
│       ├── save_structure/  # Save file components
│       │   ├── __init__.py
│       │   ├── parser.py   # Top-level save orchestration
│       │   ├── save_game.py
│       │   ├── header/
│       │   │   ├── __init__.py
│       │   │   ├── header.py
│       │   │   └── parser.py
│       │   ├── type_templates/
│       │   │   ├── __init__.py
│       │   │   ├── types.py
│       │   │   ├── template_parser.py
│       │   │   ├── type_info_parser.py
│       │   │   └── type_data_parser.py
│       │   ├── game_objects/
│       │   │   ├── __init__.py
│       │   │   ├── game_object.py
│       │   │   └── parser.py
│       │   ├── game_data/
│       │   │   ├── __init__.py
│       │   │   ├── game_data.py
│       │   │   └── parser.py
│       │   ├── world/
│       │   │   ├── __init__.py
│       │   │   ├── world.py
│       │   │   └── parser.py
│       │   ├── settings/
│       │   │   ├── __init__.py
│       │   │   ├── settings.py
│       │   │   └── parser.py
│       │   └── data_types/
│       │       ├── __init__.py
│       │       └── hashed_string.py
│       ├── binary_serializer/  # Compression handling
│       │   ├── __init__.py
│       │   └── zlib_handler.py
│       ├── const_data/        # Game constants
│       │   ├── __init__.py
│       │   ├── sim_hashes.py
│       │   ├── traits.py
│       │   └── behaviors.py
│       └── utils.py           # Helpers, validation
├── tests/
│   ├── conftest.py           # Shared pytest fixtures
│   ├── unit/                 # Fast, isolated tests
│   │   ├── test_parser.py
│   │   ├── test_header.py
│   │   ├── test_templates.py
│   │   └── ...
│   ├── integration/          # Component interaction tests
│   │   ├── test_full_parse.py
│   │   └── test_save_write.py
│   ├── round_trip/           # Idempotent validation
│   │   ├── test_round_trip.py
│   │   └── test_compression.py
│   ├── cross_validation/     # Compare with TypeScript
│   │   ├── test_cross_validation.py
│   │   └── compare_outputs.py
│   ├── fuzzing/              # Hypothesis + corrupted data
│   │   ├── test_fuzzing.py
│   │   ├── test_corrupted_saves.py
│   │   └── test_edge_cases.py
│   ├── performance/          # Benchmarks (informational)
│   │   └── test_benchmarks.py
│   ├── snapshots/            # Regression tests
│   │   └── test_snapshots.py
│   └── fixtures/             # Test data
│       ├── vanilla/          # Base game saves (7.17, 7.31, etc.)
│       ├── dlc/              # Spaced Out saves
│       ├── modded/           # Modded saves
│       ├── versions/         # Different save versions
│       └── corrupted/        # Invalid/broken saves
└── docs/
    ├── plans/                # Design documents
    ├── api.md                # API documentation
    └── development.md        # Development guide
```

### Core Components

#### 1. Binary Parser Layer

**Purpose:** Low-level binary reading and writing

```python
class BinaryParser:
    """Low-level binary reader with offset tracking."""
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read_uint32(self) -> int:
        """Read unsigned 32-bit integer (little-endian)."""
        value = struct.unpack_from('<I', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_int32(self) -> int:
        """Read signed 32-bit integer (little-endian)."""
        value = struct.unpack_from('<i', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_klei_string(self) -> str:
        """Read length-prefixed UTF-8 string (ONI format)."""
        length = self.read_int32()
        value = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return value

    def read_bytes(self, count: int) -> bytes:
        """Read raw bytes."""
        value = self.data[self.offset:self.offset+count]
        self.offset += count
        return value

    def read_compressed(self) -> bytes:
        """Decompress remaining data with zlib."""
        compressed = self.data[self.offset:]
        return zlib.decompress(compressed)
```

**BinaryWriter** mirrors this for write operations.

#### 2. Generator-Based Parsing

**Purpose:** Maintain TypeScript's trampoline pattern for pauseable parsing

```python
def parse_save_game_generator(
    options: SaveGameParserOptions
) -> Iterator[SaveGame]:
    """Generator that yields parse instructions."""
    # Parse header
    header: SaveGameHeader = yield from parse_header()

    # Validate version
    validate_version(
        header.game_info.save_major_version,
        header.game_info.save_minor_version,
        options.version_strictness
    )

    # Parse type templates
    templates: list[TypeTemplate] = yield from parse_templates()

    # Create context
    context = ParseContext(header=header, templates=templates)

    # Parse body (with optional decompression)
    if header.is_compressed:
        body = yield from read_compressed(parse_save_body(context))
    else:
        body = yield from parse_save_body(context)

    # Return complete save
    return SaveGame(
        header=header,
        templates=templates,
        **body.__dict__
    )

def parse_save_game(
    data: bytes,
    options: SaveGameParserOptions = None
) -> SaveGame:
    """Main entry point - executes the generator."""
    parser = BinaryParser(data)
    return parser.execute(parse_save_game_generator(options))
```

#### 3. Type System

**Purpose:** Handle KSerialization type templates and dynamic deserialization

```python
@dataclass
class TypeInfo:
    """Type information from KSerialization."""
    info: int  # SerializationTypeInfo byte
    template_name: str | None = None
    sub_types: list[TypeInfo] | None = None

@dataclass
class TypeTemplate:
    """Template describing a .NET class serialization."""
    name: str  # .NET class name
    fields: list[TypeTemplateMember]
    properties: list[TypeTemplateMember]

@dataclass
class TypeTemplateMember:
    """Field or property in a type template."""
    name: str
    type: TypeInfo

class SerializationTypeCode(IntEnum):
    """Type codes from KSerialization."""
    UserDefined = 0
    SByte = 1
    Byte = 2
    Boolean = 3
    Int16 = 4
    # ... (all 24 type codes)
```

#### 4. Data Structures

**Purpose:** Represent save file components with strong typing

```python
@dataclass
class SaveGame:
    """Complete ONI save file."""
    header: SaveGameHeader
    templates: list[TypeTemplate]
    world: SaveGameWorld
    settings: SaveGameSettings
    sim_data: bytes  # Opaque simulation data
    version: Version
    game_objects: list[GameObjectGroup]
    game_data: SaveGameData

@dataclass
class SaveGameHeader:
    """Save file header."""
    build_version: int
    header_version: int
    is_compressed: bool
    game_info: GameInfo

@dataclass
class GameInfo:
    """Game information from header JSON."""
    save_major_version: int
    save_minor_version: int
    dlc_id: str
    # ... other fields

@dataclass
class GameObject:
    """A game entity (duplicant, building, etc.)."""
    position: Vector3
    rotation: Quaternion
    scale: Vector3
    folder: int
    behaviors: list[Behavior]
    # ... other fields
```

### Public API

```python
# Main API functions
def parse_oni_save(
    data: bytes,
    version_strictness: Literal["none", "major", "minor"] = "minor"
) -> SaveGame:
    """Parse ONI save file from bytes.

    Args:
        data: Raw save file bytes
        version_strictness: How strict version checking should be
            - "minor": Require exact major.minor match (safest)
            - "major": Allow different minor versions
            - "none": Skip version check (may corrupt data)

    Returns:
        Parsed SaveGame object

    Raises:
        ParseError: If file is corrupted or version incompatible
    """
    ...

def write_oni_save(save: SaveGame) -> bytes:
    """Write SaveGame object to bytes.

    Args:
        save: SaveGame object to serialize

    Returns:
        Raw save file bytes (compressed if original was compressed)
    """
    ...

# Convenience functions
def load_save_file(path: str | Path) -> SaveGame:
    """Load save from file path."""
    with open(path, 'rb') as f:
        return parse_oni_save(f.read())

def save_to_file(save: SaveGame, path: str | Path) -> None:
    """Save to file path."""
    data = write_oni_save(save)
    with open(path, 'wb') as f:
        f.write(data)

# Helper utilities
def get_behavior(game_obj: GameObject, behavior_type: type[T]) -> T | None:
    """Find behavior by type on a game object."""
    ...

def get_all_minions(save: SaveGame) -> list[GameObject]:
    """Get all duplicant game objects from save."""
    group = next((g for g in save.game_objects if g.name == "Minion"), None)
    return group.game_objects if group else []
```

## Testing Strategy

### Test Categories

#### 1. Unit Tests
- Fast, isolated tests for individual functions
- Mock dependencies where needed
- Test edge cases and error conditions
- Located in `tests/unit/`

#### 2. Integration Tests
- Test component interactions
- Multi-module workflows
- Located in `tests/integration/`

#### 3. Round-Trip Tests
- **Critical validation:** Load then save produces identical output
- Primary proof of correctness
- Compare decompressed data (zlib may vary)
- Located in `tests/round_trip/`

```python
def test_round_trip_idempotent(sample_save_file):
    """Core validation: load then save produces identical output."""
    with open(sample_save_file, 'rb') as f:
        original_data = f.read()

    # Parse
    save_game = parse_oni_save(original_data)

    # Write back
    output_data = write_oni_save(save_game)

    # Decompress both for comparison
    original_decompressed = decompress_save(original_data)
    output_decompressed = decompress_save(output_data)

    assert original_decompressed == output_decompressed
```

#### 4. Cross-Validation Tests
- Compare Python parser output with TypeScript parser
- Run both on same save files
- Export structured data (JSON) and compare
- Ensures behavioral equivalence
- Located in `tests/cross_validation/`

```python
def test_matches_typescript_output(sample_save):
    """Validate Python output matches TypeScript parser."""
    # Run TypeScript parser via subprocess/Node.js
    ts_output = run_typescript_parser(sample_save)

    # Run Python parser
    py_save = parse_oni_save(sample_save)
    py_output = save_to_comparable_format(py_save)

    # Deep comparison
    assert py_output == ts_output
```

#### 5. Fuzzing & Error Handling
- Use hypothesis for property-based testing
- Test with corrupted save files
- Truncated files, invalid headers, bad compression
- Ensure graceful error messages
- Located in `tests/fuzzing/`

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=2**32-1))
def test_uint32_round_trip(value):
    """Any uint32 should round-trip correctly."""
    writer = BinaryWriter()
    writer.write_uint32(value)
    parser = BinaryParser(writer.data)
    assert parser.read_uint32() == value

def test_corrupted_header_fails_gracefully():
    """Corrupted header produces clear error."""
    bad_data = b'\x00' * 100
    with pytest.raises(ParseError, match="Invalid header"):
        parse_oni_save(bad_data)
```

#### 6. Performance Benchmarks
- Informational only (not quality gates)
- Track parse/write times
- Monitor memory usage
- Located in `tests/performance/`

```python
@pytest.mark.benchmark
def test_parse_speed(benchmark, large_save_file):
    """Benchmark parsing time."""
    benchmark(parse_oni_save, large_save_file)
```

#### 7. Snapshot/Regression Tests
- Lock in parsed structure
- Catch unintended changes
- Use pytest-snapshot or similar
- Located in `tests/snapshots/`

### Test Fixtures

**Required test saves:**
- Vanilla base game: versions 7.17, 7.22, 7.31
- Spaced Out DLC: versions 7.23, 7.25, 7.31
- Early cycle (< 100)
- Mid cycle (100-500)
- Late cycle (> 1000)
- Modded saves
- Corrupted/truncated saves
- Different compression states

**Fixture organization:**
```
tests/fixtures/
├── vanilla/
│   ├── v7.17_cycle50.sav
│   ├── v7.31_cycle500.sav
│   └── ...
├── dlc/
│   ├── v7.25_dlc_cycle100.sav
│   └── ...
├── modded/
│   └── v7.31_modded.sav
└── corrupted/
    ├── truncated.sav
    ├── bad_header.sav
    └── bad_compression.sav
```

### Quality Gates (CI/CD)

All must pass before merge:

```yaml
checks:
  - name: Type Checking
    command: mypy --strict src/

  - name: Linting
    command: ruff check src/ tests/

  - name: Formatting
    command: ruff format --check src/ tests/

  - name: Unit Tests
    command: pytest tests/unit/ -v

  - name: Integration Tests
    command: pytest tests/integration/ -v

  - name: Round-Trip Tests
    command: pytest tests/round_trip/ -v

  - name: Cross-Validation
    command: pytest tests/cross_validation/ -v

  - name: Fuzzing
    command: pytest tests/fuzzing/ --hypothesis-profile=ci

  - name: Coverage
    command: pytest --cov=oni_save_parser --cov-report=html --cov-fail-under=80

  - name: Documentation Tests
    command: pytest --doctest-modules src/
```

## Implementation Plan

### Phase 1: Foundation (Bottom Layer)
Port and test binary primitives and basic utilities:

1. **parser/errors.py** - Exception types
   - ParseError base class
   - Version mismatch errors
   - Corruption errors
   - Tests: Error creation, messages

2. **parser/parse.py** - BinaryParser class
   - read_uint32, read_int32, read_byte
   - read_klei_string, read_bytes
   - read_compressed (zlib)
   - Tests: All primitive types, edge cases

3. **parser/unparse.py** - BinaryWriter class
   - write_uint32, write_int32, write_byte
   - write_klei_string, write_bytes
   - write_compressed (zlib)
   - Tests: Round-trip all types

4. **utils.py** - Validation and hashing
   - validate_dotnet_identifier
   - get_sdbm32_lower_hash
   - Tests: Hash validation, edge cases

**Milestone:** Binary I/O working and tested

### Phase 2: Type System
Port KSerialization type handling:

5. **save_structure/type_templates/types.py**
   - TypeInfo, TypeTemplate dataclasses
   - SerializationTypeCode enum
   - Type flag helpers
   - Tests: Type construction

6. **save_structure/type_templates/type_info_parser.py**
   - parse_type_info / unparse_type_info
   - Handle generic types, arrays
   - Tests: All type codes, generics

7. **save_structure/type_templates/template_parser.py**
   - parse_templates / unparse_templates
   - Template validation
   - Tests: Template round-trip

8. **save_structure/type_templates/type_data_parser.py**
   - parse_by_template / unparse_by_template
   - Dynamic deserialization
   - Tests: All serialization types

**Milestone:** Type system working, can parse templates

### Phase 3: Core Structures
Port header and basic structures:

9. **save_structure/header/header.py**
   - SaveGameHeader, GameInfo dataclasses
   - Tests: Header construction

10. **save_structure/header/parser.py**
    - parse_header / unparse_header
    - JSON decoding/encoding
    - Tests: Header round-trip, versions

11. **save_structure/data_types/**
    - HashedString implementation
    - Other custom data types
    - Tests: SDBM hash validation

12. **binary_serializer/**
    - Compression handling
    - Tests: Compression round-trip

**Milestone:** Can parse headers and type templates

### Phase 4: Game Data
Port game content structures:

13. **save_structure/world/**
    - World data (preserve as-is)
    - Tests: Preserve world data unchanged

14. **save_structure/settings/**
    - Game settings
    - Tests: Settings round-trip

15. **save_structure/game_objects/**
    - GameObject, GameObjectGroup
    - Behavior parsing
    - Tests: Game object round-trip, behavior extraction

16. **save_structure/game_data/**
    - Additional game state
    - Tests: Game data round-trip

17. **save_structure/parser.py**
    - Top-level orchestration
    - parse_save_game / unparse_save_game
    - Tests: Full round-trip on real saves

**Milestone:** Complete save parsing working

### Phase 5: API & Polish
Public interface and conveniences:

18. **__init__.py**
    - Public API exports
    - Convenience functions
    - Tests: API usage examples

19. **const_data/**
    - SimHashes, traits, behaviors
    - Game constants
    - Tests: Constant lookups

**Milestone:** Library ready for use

### Validation Checkpoints

After each phase:
1. All unit tests pass
2. Relevant round-trip tests pass
3. Cross-validation with TypeScript passes
4. Code coverage ≥ 80%
5. Type checking passes (mypy --strict)
6. Linting passes (ruff)

## Future Enhancements

After initial port is complete and proven:

1. **Pythonic Refactoring**
   - Context managers for file handling
   - Properties for accessor patterns
   - Cleaner iteration patterns
   - Type narrowing with match statements

2. **API Improvements**
   - More helper utilities
   - Query/filter capabilities
   - Fluent API for modifications

3. **Performance Optimization**
   - Profile hot paths
   - Optimize if needed (after proving correctness)

4. **Extended Features**
   - Save validation tools
   - Diff/comparison utilities
   - Statistical analysis helpers
   - Save file repair tools

5. **Documentation**
   - API reference
   - Usage examples
   - Tutorial notebooks
   - Format specification

## Success Metrics

The implementation will be considered successful when:

- ✅ All quality gates pass (type checking, linting, coverage)
- ✅ Round-trip tests pass on 20+ diverse save files
- ✅ Cross-validation shows 100% match with TypeScript parser
- ✅ Fuzzing reveals no crashes or data corruption
- ✅ API is documented with examples
- ✅ Package is installable via pip/uv
- ✅ CI/CD pipeline is green

## Non-Goals

These are explicitly out of scope for the initial implementation:

- ❌ Performance matching TypeScript (informational only)
- ❌ Understanding world data format (preserve as-is)
- ❌ Creating new saves from scratch
- ❌ Async/concurrent parsing
- ❌ GUI or CLI tools (library only)
- ❌ Python < 3.12 support

## References

- Original TypeScript library: https://github.com/RoboPhred/oni-save-parser
- Background documentation: ../background.md
- ONI Wiki: https://oxygennotincluded.wiki.gg/
- Klei Forums: https://forums.kleientertainment.com/

## Appendix: Development Commands

```bash
# Setup
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Testing
uv run pytest                              # All tests
uv run pytest tests/unit/                  # Unit tests only
uv run pytest tests/round_trip/            # Round-trip validation
uv run pytest --cov=oni_save_parser        # With coverage

# Quality
uv run mypy --strict src/                  # Type checking
uv run ruff check src/ tests/              # Linting
uv run ruff format src/ tests/             # Formatting

# Benchmarks
uv run pytest tests/performance/ --benchmark-only
```
