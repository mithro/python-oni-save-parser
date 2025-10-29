# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-30

### Added
- Complete Python port of ONI save parser from TypeScript
- Support for all 24 KSerialization type codes
- Binary parser with full type support (int8-int64, float, double, bool)
- Type template parsing for .NET object deserialization
- Save file header parsing (versions 0 and 1+)
- Compressed save file support (zlib)
- World data and game settings parsing
- Complete game objects parsing:
  - GameObject with position, rotation, scale
  - GameObjectBehavior (components) with template-based parsing
  - GameObjectGroup (prefab organization)
- High-level API:
  - `load_save_file()` - Load save from disk
  - `save_to_file()` - Write save to disk
  - `get_colony_info()` - Extract colony metadata
  - `get_game_objects_by_prefab()` - Filter objects by type
  - `list_prefab_types()` - List all prefab types
  - `get_prefab_counts()` - Count objects by prefab
- Command-line interface:
  - `oni-save-parser info` - Display colony information
  - `oni-save-parser prefabs` - List prefabs with counts
  - JSON output support
  - Version checking with `--allow-minor-mismatch`
- Comprehensive test suite:
  - 183 unit tests with 92.39% coverage
  - 14 performance benchmarks
  - Property-based testing with Hypothesis
  - Round-trip validation tests
- Complete documentation:
  - README with examples and API reference
  - Architecture overview
  - Development guide
  - Example scripts (`examples/basic_usage.py`)
- Type safety:
  - Full type hints throughout codebase
  - Strict mypy validation
  - No type: ignore comments
- Error handling:
  - Custom exception types (ParseError, CorruptionError, VersionMismatchError)
  - Offset tracking in errors
  - Validation at all parsing levels

### Performance
- API operations: ~400-700ns
- Small saves (125 objects): ~600μs parse, ~850μs serialize
- Medium saves (1,110 objects): ~5.5ms parse, ~3.2ms serialize
- Large saves (5,520 objects): ~30ms parse, ~15ms serialize

### Technical Details
- Python 3.12+ required
- No runtime dependencies (pure Python)
- Development dependencies: pytest, mypy, ruff, pytest-cov, pytest-benchmark, hypothesis
- Idempotent design: round-trip parsing preserves byte-identical output
- Unknown data preserved as raw bytes for forward compatibility

### Credits
- Based on [oni-save-parser](https://github.com/robophred/oni-save-parser) by robophred (TypeScript)
- Python port by Claude Code with guidance from mithro
- Oxygen Not Included is developed by Klei Entertainment
