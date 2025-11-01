# ONI Map Rendering

This document describes the map rendering functionality for Oxygen Not Included save files.

## Overview

The rendering module transforms ONI save files into visual PNG images, showing the layout of asteroids including elements, materials, and structures. This is useful for:

- Visualizing base layouts
- Analyzing map composition
- Creating shareable map images
- Debugging save file data

## Quick Start

### Command Line Interface

The simplest way to render a save file is using the provided CLI tool:

```bash
# Render all asteroids from a save file
uv run python examples/render_map.py save.sav --output-dir renders/

# Render with larger scale (4x4 pixels per tile)
uv run python examples/render_map.py save.sav --output-dir renders/ --scale 4
```

### Python API

You can also use the rendering API directly in Python:

```python
from pathlib import Path
from oni_save_parser.rendering.pipeline import MapRenderer

# Create renderer
renderer = MapRenderer()

# Render all asteroids from a save file
output_files = renderer.render(
    save_path="save.sav",
    output_dir="renders",
    scale=2,
)

print(f"Rendered {len(output_files)} asteroids")
for file_path in output_files:
    print(f"  {file_path}")
```

## Features

### Supported Elements

The renderer supports all ONI elements with fallback colors for visualization:

- **Solids**: Granite, Sandstone, Igneous Rock, Obsidian, Abyssalite, etc.
- **Liquids**: Water, Polluted Water, Crude Oil, Petroleum, Magma, etc.
- **Gases**: Oxygen, Hydrogen, Natural Gas, Carbon Dioxide, Chlorine, etc.

Colors are based on the game's visual representation to make the output intuitive.

### Output Format

- **Format**: PNG (RGB)
- **Filename Pattern**: `{colony-name}_cycle-{number}_asteroid-{id}-{name}.png`
- **Scale**: Configurable from 1x to 10x pixels per tile (default: 2x)
- **One file per asteroid**: Multi-asteroid saves generate multiple files

### Example Output Filenames

```
New-Colony_cycle-010_asteroid-0-MiniBaseStart.png
New-Colony_cycle-010_asteroid-1-MiniForestFrozenStart.png
```

## Architecture

The rendering system is organized into a three-stage pipeline:

### Stage 1: Parse
Loads the binary save file and deserializes it into raw game data structures.

```python
from oni_save_parser import load_save_file
save_data = load_save_file("save.sav")
```

### Stage 2: Transform
Converts raw game data into a rendering-optimized data model.

```python
from oni_save_parser.rendering.transformers import DataTransformer
from oni_save_parser.assets.element_registry import ElementRegistry

element_registry = ElementRegistry()
transformer = DataTransformer(element_registry)
world_model = transformer.transform(save_data)
```

This stage:
- Extracts metadata (colony name, cycle number, etc.)
- Processes each asteroid's cell grid
- Resolves element types from hash IDs
- Creates a clean data model for rendering

### Stage 3: Render
Converts the data model into PNG images.

```python
from oni_save_parser.rendering.static_renderer import StaticRenderer

renderer = StaticRenderer(element_registry, scale=2)
for asteroid in world_model.asteroids:
    renderer.render_asteroid(asteroid, "output.png")
```

This stage:
- Creates an RGB image for each asteroid
- Colors each cell based on element type and state
- Scales the output according to the scale parameter
- Saves to PNG files

## Module Structure

### Core Modules

#### `pipeline.py` - MapRenderer
The main orchestrator that coordinates the three-stage pipeline.

**Key Class**: `MapRenderer`
- `__init__()`: Initialize renderer with element registry
- `render(save_path, output_dir, scale)`: Render all asteroids to PNG files

#### `transformers.py` - DataTransformer
Converts raw save data to rendering-optimized models.

**Key Class**: `DataTransformer`
- `transform(save_data)`: Convert save data to WorldModel
- Extracts metadata from save file
- Processes asteroid grids and cells
- Resolves element types

#### `static_renderer.py` - StaticRenderer
Renders data models to static PNG images.

**Key Class**: `StaticRenderer`
- `__init__(element_registry, scale)`: Initialize with element registry and scale
- `render_asteroid(asteroid, output_path)`: Render single asteroid to PNG

#### `cell_renderer.py` - CellRenderer
Renders individual cells based on element state.

**Key Class**: `CellRenderer`
- `render_cell(cell)`: Returns RGB color for a cell based on element and state

#### `models.py` - Data Models
Type-safe data structures for rendering.

**Key Models**:
- `ElementState`: Enum for Solid, Liquid, Gas, Vacuum
- `Cell`: Single tile data (element, temperature, mass, state)
- `AsteroidData`: Full asteroid data (id, name, dimensions, cells)
- `SaveMetadata`: Save file metadata (colony name, cycle, etc.)
- `WorldModel`: Complete world data (metadata + asteroids)

### Element Resolution

The system uses `ElementRegistry` to map element hash IDs to human-readable names and colors:

```python
from oni_save_parser.assets.element_registry import ElementRegistry

registry = ElementRegistry()
element_name = registry.get_element_name(hash_id)
color = registry.get_element_color(element_name)
```

The registry provides:
- Hash ID to element name mapping
- Element to color mapping (fallback colors in Phase 1)
- Future support for loading game assets

## Configuration

### Scale Parameter

The `scale` parameter controls how many pixels represent each tile:

- **Scale 1**: 1x1 pixels per tile (most compact)
- **Scale 2**: 2x2 pixels per tile (default, good balance)
- **Scale 4**: 4x4 pixels per tile (more detail)
- **Scale 10**: 10x10 pixels per tile (maximum detail)

Example image dimensions for a 256x384 asteroid:
- Scale 1: 256x384 pixels
- Scale 2: 512x768 pixels
- Scale 4: 1024x1536 pixels

### Element Colors

Colors are currently hardcoded as fallback values in `src/oni_save_parser/assets/fallback_colors.py`. Future phases will support loading actual game asset colors.

You can customize colors by editing the `FALLBACK_ELEMENT_COLORS` dictionary:

```python
FALLBACK_ELEMENT_COLORS: dict[str, tuple[int, int, int]] = {
    "Oxygen": (0, 180, 255),     # Cyan-blue
    "Granite": (128, 128, 128),  # Gray
    # ... add more elements
}
```

## Testing

The rendering module includes comprehensive tests:

### Unit Tests
Located in `tests/rendering/`:
- `test_models.py`: Data model validation
- `test_cell_renderer.py`: Cell rendering logic
- `test_static_renderer.py`: Static PNG rendering
- `test_transformers.py`: Data transformation
- `test_pipeline.py`: End-to-end pipeline

### Integration Tests
Located in `tests/integration/`:
- `test_full_pipeline.py`: Full pipeline with real save files
- `test_render_map_cli.py`: CLI tool integration

Run tests with:
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src/oni_save_parser/rendering

# Run only rendering tests
uv run pytest tests/rendering/ tests/integration/test_full_pipeline.py
```

### Test Coverage

Current coverage: **92%** (exceeds 80% target)

Coverage by module:
- `cell_renderer.py`: 100%
- `models.py`: 100%
- `pipeline.py`: 100%
- `static_renderer.py`: 95%
- `transformers.py`: 81%

## Type Safety

The rendering module uses strict type checking with mypy:

```bash
# Run type checking
uv run mypy src/oni_save_parser/rendering/ --strict
```

All modules pass strict type checking with:
- Full type annotations
- No `Any` types
- Strict optional checking
- Proper return types

## Limitations & Future Work

### Current Limitations

1. **Phase 1 Implementation**: Uses fallback colors only (no game assets)
2. **Static Rendering**: No support for overlays or layers
3. **No Temperature Visualization**: Elements rendered by type only
4. **No Building Rendering**: Only terrain/elements are shown

### Planned Enhancements

#### Phase 2: Game Asset Integration
- Load actual element colors from game files
- Support for building sprites
- Proper material textures

#### Phase 3: Advanced Features
- Temperature overlays (heat maps)
- Pressure visualization
- Layer controls (elements, buildings, etc.)
- Interactive HTML output
- Animation support (time-lapse)

## Performance

The rendering pipeline is optimized for performance:

- **Small saves** (cycle 10): ~0.5 seconds
- **Medium saves** (cycle 150): ~2 seconds
- **Large saves** (cycle 1000+): ~5-10 seconds

Performance scales linearly with:
- Number of asteroids
- Asteroid dimensions
- Scale parameter (higher scale = larger images = slightly slower I/O)

## Troubleshooting

### Common Issues

**Issue**: "Failed to load image pixels"
- **Cause**: Pillow failed to create image buffer
- **Solution**: Check available memory, try smaller scale

**Issue**: Color appears as gray/default
- **Cause**: Element not in fallback color dictionary
- **Solution**: Add element to `FALLBACK_ELEMENT_COLORS` in `fallback_colors.py`

**Issue**: Output file not found
- **Cause**: Permission issues or invalid path
- **Solution**: Check directory permissions, ensure parent directory exists

**Issue**: Save file parsing fails
- **Cause**: Incompatible save version or corrupted file
- **Solution**: Check save file version, try with different save

### Debug Mode

Enable debug output by importing logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

### Render Multiple Saves

```python
from pathlib import Path
from oni_save_parser.rendering.pipeline import MapRenderer

renderer = MapRenderer()

# Render all saves in a directory
save_dir = Path("test_saves")
for save_file in save_dir.glob("*.sav"):
    print(f"Rendering {save_file.name}...")
    output_dir = Path("renders") / save_file.stem
    renderer.render(save_file, output_dir, scale=2)
```

### Custom Scaling

```python
# Create multiple scales for comparison
for scale in [1, 2, 4]:
    output_dir = Path(f"renders/scale_{scale}")
    renderer.render("save.sav", output_dir, scale=scale)
```

### Extract Specific Asteroid

```python
from oni_save_parser import load_save_file
from oni_save_parser.rendering.transformers import DataTransformer
from oni_save_parser.rendering.static_renderer import StaticRenderer
from oni_save_parser.assets.element_registry import ElementRegistry

# Load and transform
save_data = load_save_file("save.sav")
registry = ElementRegistry()
transformer = DataTransformer(registry)
world_model = transformer.transform(save_data)

# Render only the first asteroid
renderer = StaticRenderer(registry, scale=4)
first_asteroid = world_model.asteroids[0]
renderer.render_asteroid(first_asteroid, "asteroid_0.png")
```

## API Reference

### MapRenderer

```python
class MapRenderer:
    def __init__(self) -> None:
        """Initialize the renderer pipeline."""

    def render(
        self,
        save_path: Path | str,
        output_dir: Path | str,
        scale: int = 2,
    ) -> list[str]:
        """
        Render all asteroids from a save file to PNG images.

        Args:
            save_path: Path to .sav file
            output_dir: Directory for output PNG files
            scale: Pixels per tile (1-10)

        Returns:
            List of output file paths created
        """
```

### StaticRenderer

```python
class StaticRenderer:
    def __init__(
        self,
        element_registry: ElementRegistry,
        scale: int = 2,
    ) -> None:
        """
        Initialize static renderer.

        Args:
            element_registry: Element registry for colors
            scale: Pixels per tile (1-10)
        """

    def render_asteroid(
        self,
        asteroid: AsteroidData,
        output_path: Path | str,
    ) -> None:
        """
        Render an asteroid to a PNG file.

        Args:
            asteroid: Asteroid data to render
            output_path: Output file path
        """
```

### DataTransformer

```python
class DataTransformer:
    def __init__(self, element_registry: ElementRegistry) -> None:
        """Initialize transformer with element registry."""

    def transform(self, save_data: SaveGame) -> WorldModel:
        """
        Transform save data to world model.

        Args:
            save_data: Parsed save game data

        Returns:
            WorldModel containing all asteroids and metadata
        """
```

## Contributing

When contributing to the rendering module:

1. **Add tests** for all new features
2. **Run type checking** with mypy --strict
3. **Maintain coverage** above 80%
4. **Update documentation** for API changes
5. **Follow existing patterns** in the codebase

See the implementation plan in `docs/plans/2025-11-01-map-rendering.md` for architecture decisions and future roadmap.
