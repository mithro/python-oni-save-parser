# Contributing to ONI Save Parser

Thank you for your interest in contributing to the ONI Save Parser! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/mithro/oni-save-parser.git
cd oni-save-parser

# Create worktree for Python parser development
git worktree add .worktrees/python-parser feature/python-parser
cd .worktrees/python-parser

# Install dependencies
uv sync --all-extras
```

## Development Workflow

### Before You Start

1. Create a new branch from `feature/python-parser`:
   ```bash
   git checkout -b your-feature-name feature/python-parser
   ```

2. Make sure all tests pass:
   ```bash
   uv run pytest tests/ -v
   ```

### Making Changes

1. **Write tests first** (Test-Driven Development):
   - Add tests in `tests/unit/` for new functionality
   - Ensure tests fail before implementing the feature
   - Implement the feature
   - Verify tests pass

2. **Follow code style**:
   - Use type hints for all function signatures
   - Follow existing code organization
   - Keep functions focused and small
   - Add docstrings for public APIs

3. **Run quality checks**:
   ```bash
   # Run all tests
   uv run pytest tests/ -v

   # Check test coverage (should be >80%)
   uv run pytest tests/ --cov=src/oni_save_parser --cov-report=term-missing

   # Type checking (must pass with no errors)
   uv run mypy src/oni_save_parser

   # Format code
   uv run ruff format src/ tests/

   # Lint code
   uv run ruff check src/ tests/
   ```

4. **Run benchmarks** (if performance-critical changes):
   ```bash
   uv run pytest tests/benchmark --benchmark-only
   ```

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed, explaining:
- Why this change is needed
- What problem it solves
- Any breaking changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Your Name <your.email@example.com>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or modifications
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Example:
```
feat(api): add function to extract duplicant data

Add get_duplicants() function to extract duplicant information
from game objects including names, traits, and positions.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Jane Developer <jane@example.com>
```

### Pull Requests

1. Ensure all tests pass and coverage remains high (>80%)
2. Update documentation if adding new features
3. Add entry to CHANGELOG.md under "Unreleased" section
4. Provide clear description of changes and motivation
5. Link any related issues

## Code Style Guide

### Type Hints

Always use type hints:

```python
# Good
def parse_value(data: bytes, offset: int) -> tuple[int, int]:
    """Parse value from bytes at offset.

    Args:
        data: Byte data to parse
        offset: Starting position

    Returns:
        Tuple of (parsed_value, new_offset)
    """
    ...

# Bad - no type hints
def parse_value(data, offset):
    ...
```

### Error Handling

Use custom exception types with context:

```python
from oni_save_parser.parser.errors import ParseError

# Good
if offset >= len(data):
    raise ParseError(
        f"Cannot read beyond data end (offset: {offset}, length: {len(data)})",
        offset=offset
    )

# Bad
if offset >= len(data):
    raise Exception("Cannot read")
```

### Testing

Write comprehensive tests:

```python
def test_parse_value_success():
    """Should parse value from valid data."""
    data = b"\x2A\x00\x00\x00"
    result = parse_int32(data, 0)
    assert result == 42

def test_parse_value_insufficient_data():
    """Should raise ParseError when data is too short."""
    data = b"\x2A\x00"
    with pytest.raises(ParseError) as exc_info:
        parse_int32(data, 0)
    assert "insufficient data" in str(exc_info.value).lower()
```

## Areas for Contribution

### High Priority

1. **Game Data Parsing**: Implement parser for `game_data` section (currently raw bytes)
2. **Behavior Extra Data**: Parse special data for Storage, MinionModifiers, Modifiers behaviors
3. **Real Save Testing**: Test with actual ONI save files and report issues
4. **Performance**: Optimize hot paths identified by benchmarks

### Medium Priority

1. **CLI Enhancements**: Additional commands (extract, modify, validate)
2. **API Additions**: More convenience functions for common use cases
3. **Documentation**: More examples, tutorials, architecture diagrams
4. **Type Stubs**: Add py.typed marker and verify stub generation

### Low Priority

1. **Web Interface**: Browser-based save file viewer/editor
2. **Save Diffing**: Compare two saves and show changes
3. **Mod Support**: Parse and handle modded content

## Testing Guidelines

### Unit Tests

- Place in `tests/unit/` matching source structure
- Test happy path and error cases
- Use descriptive test names
- Aim for >90% coverage

### Benchmarks

- Place in `tests/benchmark/`
- Test realistic scenarios
- Document expected performance
- Compare before/after for optimizations

### Property-Based Tests

Use Hypothesis for complex scenarios:

```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.binary(min_size=4, max_size=100))
def test_round_trip_binary_data(data):
    """Should preserve arbitrary binary data through round-trip."""
    writer = BinaryWriter()
    writer.write_bytes(data)
    parser = BinaryParser(writer.data)
    assert parser.read_bytes(len(data)) == data
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def load_save_file(
    file_path: str | Path,
    verify_version: bool = True,
    allow_minor_mismatch: bool = True
) -> SaveGame:
    """Load an ONI save file from disk.

    Args:
        file_path: Path to .sav file
        verify_version: Check save version compatibility
        allow_minor_mismatch: Allow different minor versions

    Returns:
        Parsed save game structure

    Raises:
        FileNotFoundError: If file doesn't exist
        VersionMismatchError: If version is incompatible
        CorruptionError: If save data is corrupted

    Example:
        >>> save = load_save_file("MySave.sav")
        >>> print(f"Colony: {save.header.game_info.base_name}")
    """
    ...
```

### README Updates

Update README.md when adding:
- New features
- API functions
- CLI commands
- Configuration options

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Review the code and tests for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
