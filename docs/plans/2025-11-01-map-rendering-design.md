# ONI Save File Map Renderer - Design Document

**Date**: 2025-11-01
**Status**: Design Complete, Implementation Pending

## Overview

A map rendering system for Oxygen Not Included save files that generates visual representations of game worlds. The system will support both static PNG images (for sharing and documentation) and future interactive HTML visualizations (for analysis and exploration).

## Goals

1. **Base Sharing**: Generate shareable images of colony layouts for documentation and online sharing
2. **Colony Analysis**: Visualize base layouts to identify issues and plan improvements
3. **Timelapse/Comparison**: Enable comparison of saves across time to track colony evolution
4. **Multi-Asteroid Support**: Handle full DLC saves with multiple asteroids

## Requirements Summary

### Outputs
- **Static PNG images** via Python/Pillow (Phase 1)
- **Interactive HTML** via web technologies (Future phase)

### Content
- Full terrain rendering with accurate element colors
- Iconic representations for buildings
- Iconic representations for duplicants and creatures
- Separate output image per asteroid

### Technical Constraints
- Use existing `oni_save_parser` library for save file parsing
- Extract actual element colors from ONI game installation when available
- Fallback to hardcoded colors when game assets unavailable
- Support Python-based rendering (Pillow/PIL)

### Scale
- Full multi-asteroid save support (DLC compatible)
- Handle large maps efficiently (256×384 tiles per asteroid, 5+ asteroids possible)

## Architecture: Pipeline-Based System

The renderer follows a **four-stage pipeline architecture** for maximum flexibility and extensibility:

```
.sav file → Parse → Transform → Layout → Render → output files
```

### Stage 1: Parse
- Extracts raw save data using existing `oni_save_parser` library
- Loads all game objects (cells, buildings, entities, world data) into memory
- Wrapper around existing parser functionality

### Stage 2: Transform
- Normalizes parsed data into unified intermediate representation (`WorldModel`)
- Maps element IDs to colors/textures via `ElementRegistry`
- Identifies building types and assigns icon references
- Locates duplicants and creatures with positions
- Organizes multi-asteroid data into separate world instances

### Stage 3: Layout
- Determines output arrangement (minimal for separate images per asteroid)
- Calculates output dimensions based on asteroid size and scale factor
- Handles output file naming with asteroid identifiers

### Stage 4: Render
- Takes `WorldModel` and produces output files
- **StaticRenderer**: Uses Pillow to draw tiles, overlay icons, export PNG
- **InteractiveRenderer**: (Future) Generates HTML with Canvas/SVG for zoom/pan/tooltips

### Benefits of Pipeline Architecture
- Each stage is independent and testable
- Easy to add new renderers without touching parse/transform
- Layout strategies can be swapped without code changes
- Transform stage serves both static and interactive outputs

## Data Model

### WorldModel (Intermediate Representation)

```python
class WorldModel:
    asteroids: List[AsteroidData]  # Multiple worlds for DLC saves
    metadata: SaveMetadata         # Cycle number, colony name, seed

class SaveMetadata:
    colony_name: str
    cycle_number: int
    seed: str

class AsteroidData:
    id: str
    name: str              # "Terra", "Swamp", "Frozen", etc.
    width: int
    height: int
    cells: Grid[Cell]      # 2D array of terrain
    buildings: List[Building]
    entities: List[Entity]

class Cell:
    element: ElementType   # Oxygen, Granite, Water, etc.
    state: ElementState    # SOLID, LIQUID, or GAS
    temperature: float
    mass: float

class Building:
    type: str              # "Outhouse", "Generator", etc.
    position: (x, y)
    size: (w, h)
    icon_id: str          # Maps to icon shape/color

class Entity:
    type: str             # "Duplicant", "Hatch", etc.
    name: str            # For duplicants
    position: (x, y)
    icon_id: str
```

### Element Registry

```python
class ElementRegistry:
    """Maps element IDs to visual properties"""

    def __init__(self, asset_loader: GameAssetLoader):
        self.colors = {}        # element_id → RGB color
        self.load_from_assets(asset_loader)
        self.load_fallbacks()   # Hardcoded palette

    def get_color(self, element: ElementType) -> RGB:
        """Returns game color or fallback"""
```

### Icon Registry

```python
class IconRegistry:
    """Maps building/entity types to icon representations"""

    def get_icon(self, type_id: str) -> IconDefinition:
        """Returns geometric shape definition (circle, square, triangle)"""
```

## Tile Rendering System

### Single-State Per Tile (Corrected)

Each grid cell contains **only one element** in one state (solid, liquid, OR gas). No layering required.

```python
class CellRenderer:
    def render_cell(self, cell: Cell) -> Pixel:
        # Get base color from element registry
        color = self.element_registry.get_color(cell.element)

        # Apply state-based visual treatment
        if cell.state == ElementState.LIQUID:
            return self.apply_liquid_effect(color)
        elif cell.state == ElementState.GAS:
            return self.apply_gas_effect(color)
        else:  # SOLID
            return color

    def apply_liquid_effect(self, color: RGB) -> RGB:
        """Slight brightness adjustment for liquids"""

    def apply_gas_effect(self, color: RGB) -> RGB:
        """Lighter appearance for gases"""
```

### Visual State Distinctions
- **Solids**: Opaque, full color from game data
- **Liquids**: Slight brightness adjustment
- **Gases**: Lighter/more transparent appearance

### Game Asset Loading

```python
class GameAssetLoader:
    """Extracts element definitions from ONI installation"""

    def __init__(self, game_install_path: str):
        self.game_path = game_install_path

    def load_element_colors(self) -> Dict[str, RGB]:
        """Parse game data files for element colors"""
        # Extract from YAML or other game data formats
```

### Fallback Strategy
- If game installation path not found or invalid
- Use hardcoded color palette for common elements
- Warn user but continue rendering
- Log which elements couldn't be mapped
- Unknown elements render as magenta for visibility

## Pipeline Execution

### Orchestrator

```python
class MapRenderer:
    def __init__(self, game_assets_path: Optional[str] = None):
        self.asset_loader = GameAssetLoader(game_assets_path) if game_assets_path else None
        self.element_registry = ElementRegistry(self.asset_loader)
        self.icon_registry = IconRegistry()

    def render(self, save_path: str, output_dir: str,
               scale: int = 2,
               show_buildings: bool = False,
               show_entities: bool = False) -> List[str]:
        """
        Render all asteroids from save file.
        Returns list of output file paths.
        """
        # Stage 1: Parse
        raw_data = SaveParser.parse(save_path)

        # Stage 2: Transform
        transformer = DataTransformer(self.element_registry, self.icon_registry)
        world_model = transformer.transform(raw_data)

        # Stage 3: Layout (minimal - just compute dimensions)
        layout_engine = LayoutEngine()

        # Stage 4: Render each asteroid separately
        renderer = StaticRenderer(self.element_registry, self.icon_registry, scale)
        output_files = []

        for asteroid in world_model.asteroids:
            layout = layout_engine.compute_layout(asteroid, scale)
            output_path = self._build_output_path(
                output_dir, world_model.metadata, asteroid
            )
            renderer.render_asteroid(
                asteroid, layout, output_path,
                show_buildings=show_buildings,
                show_entities=show_entities
            )
            output_files.append(output_path)

        return output_files

    def _build_output_path(self, output_dir: str,
                          metadata: SaveMetadata,
                          asteroid: AsteroidData) -> str:
        """Generate output filename"""
        filename = f"{metadata.colony_name}_cycle-{metadata.cycle_number}_asteroid-{asteroid.id}-{asteroid.name}.png"
        return os.path.join(output_dir, filename)
```

### Key Design Decisions
- `ElementRegistry` shared across all stages - single source of truth
- Each stage is stateless - can be tested independently
- Separate image per asteroid simplifies layout
- Scale factor applied at render time, not in data model

## File Organization

```
src/oni_save_parser/
  rendering/
    __init__.py
    pipeline.py              # MapRenderer orchestrator
    parsers.py               # SaveParser wrapper
    transformers.py          # DataTransformer, WorldModel classes
    layout.py                # LayoutEngine
    static_renderer.py       # StaticRenderer (Pillow-based)
    cell_renderer.py         # CellRenderer with state-based rendering

  assets/
    __init__.py
    game_asset_loader.py     # GameAssetLoader
    element_registry.py      # ElementRegistry
    icon_registry.py         # IconRegistry
    fallback_colors.py       # Hardcoded color palette

examples/
  render_map.py              # CLI tool for rendering maps

tests/
  rendering/
    test_cell_renderer.py
    test_transformers.py
    test_static_renderer.py
    test_pipeline.py
    fixtures/
      expected/              # Reference images for regression testing
```

## CLI Interface

### Command: `examples/render_map.py`

```bash
# Basic usage - render all asteroids from a save
uv run python examples/render_map.py save.sav --output-dir renders/

# Specify ONI game install path for accurate colors
uv run python examples/render_map.py save.sav \
    --game-path ~/.steam/steam/steamapps/common/OxygenNotIncluded \
    --output-dir renders/

# With optional features
uv run python examples/render_map.py save.sav \
    --output-dir renders/ \
    --scale 4 \
    --show-buildings \
    --show-entities \
    --show-grid
```

### CLI Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `save_path` | positional | required | Path to .sav file |
| `--output-dir` | str | `./renders/` | Output directory for PNG files |
| `--game-path` | str | None | ONI installation path for game assets |
| `--scale` | int | 2 | Pixels per tile (1-10) |
| `--show-buildings` | flag | False | Include building icons |
| `--show-entities` | flag | False | Include duplicant/critter icons |
| `--show-grid` | flag | False | Draw grid lines |
| `--format` | str | `png` | Output format (png or jpg) |

### Output Naming Convention

```
{colony-name}_cycle-{number}_asteroid-{id}-{name}.{format}

Examples:
  MyColony_cycle-123_asteroid-1-terra.png
  MyColony_cycle-123_asteroid-2-swamp.png
  MyColony_cycle-123_asteroid-3-frozen.png
```

## Error Handling

### Missing Game Assets
- If ONI installation path not found or invalid
- **Fallback**: Use hardcoded color palette for common elements
- **Action**: Warn user but continue rendering
- **Logging**: Log which elements couldn't be mapped to game colors

### Corrupted/Invalid Save Files
- Parser fails to read save data
- **Action**: Catch parsing exceptions, provide clear error message
- **User Guidance**: Suggest verifying save file loads in ONI game

### Extremely Large Maps
- DLC saves can have 5+ asteroids, each 256×384 tiles
- Memory concern: ~500k tiles
- **Solution**: Render asteroids one at a time (already doing this)
- **Future**: Optional downsampling for preview mode

### Missing Element/Building Definitions
- Save contains modded content or unknown IDs
- **Action**: Render as magenta "unknown" tile/icon
- **Logging**: Log unknown IDs for debugging

### PNG Size Limits
- PNG format supports huge images
- Practical limit: ~8192px
- **Solution**: Already rendering separate images per asteroid
- **Option**: Provide downscaling parameter if needed

## Testing Strategy

### Unit Tests

#### CellRenderer Tests (`tests/rendering/test_cell_renderer.py`)
- Single solid element → correct color from registry
- Liquid element → brightness adjustment applied
- Gas element → lighter appearance
- Unknown element ID → fallback magenta color + logged warning

#### DataTransformer Tests (`tests/rendering/test_transformers.py`)
- Parse minimal save → correct WorldModel structure
- Multi-asteroid save → multiple AsteroidData objects
- Cell element/state extraction → correct ElementState enum
- Building extraction → correct positions and types
- Entity extraction → duplicants and critters identified

#### ElementRegistry Tests (`tests/rendering/test_element_registry.py`)
- Load from game assets → element colors mapped correctly
- Missing game assets → fallback colors loaded
- Query known element → correct color returned
- Query unknown element → fallback color + warning logged

### Integration Tests

#### End-to-End Rendering (`tests/rendering/test_pipeline.py`)
- Use test fixture saves from `test_saves/` directory
  - `01-early-game-cycle-010.sav`
  - `02-mid-game-cycle-148.sav`
  - `03-late-game-cycle-1160.sav`
- Render to PNG
- Verify output image dimensions match expected (width × height × scale)
- Visual regression: compare against reference images
  - Pixel difference threshold for acceptable variation
  - Store reference images in `tests/rendering/fixtures/expected/`

#### Multi-Asteroid Rendering
- DLC save with 3+ asteroids → separate PNG files generated
- Verify each asteroid file exists
- Check dimensions correct for each asteroid
- Verify filenames include asteroid names/IDs

### Test Fixtures
- **Minimal synthetic saves**: Known content (specific elements at coordinates)
- **Real-world examples**: Existing `test_saves/` directory
- **Reference images**: `tests/rendering/fixtures/expected/` for visual regression

### Manual Testing Checklist
- [ ] Render each test save, visually inspect for correctness
- [ ] Compare against in-game screenshots
- [ ] Verify building icons align with tile grid
- [ ] Check entity positions are accurate
- [ ] Test with and without game assets path
- [ ] Verify fallback colors work when game path missing

## Implementation Phases

### Phase 1: Foundation (MVP)
**Goal**: Render terrain-only map of single asteroid as PNG

**Components**:
- `GameAssetLoader` with fallback colors
- `ElementRegistry` with basic color mapping
- `SaveParser` wrapper around existing parser
- `DataTransformer`: save data → WorldModel
- `CellRenderer`: single-state tile rendering
- `StaticRenderer`: basic Pillow PNG output
- Simple CLI: render single asteroid, terrain only

**Acceptance Criteria**:
- Can load a save file
- Can render terrain to PNG with correct colors
- Fallback colors work without game assets
- Basic tests passing

### Phase 2: Multi-Asteroid Support
**Goal**: Render all asteroids from DLC saves as separate PNGs

**Components**:
- Update `DataTransformer` to handle multiple asteroids
- `LayoutEngine` (minimal - compute dimensions only)
- Output naming with asteroid names/IDs
- CLI: render all asteroids automatically

**Acceptance Criteria**:
- DLC saves with multiple asteroids produce multiple PNG files
- Each file named correctly with asteroid identifier
- All asteroids rendered at same scale

### Phase 3: Buildings & Entities
**Goal**: Maps show buildings and entities with iconic representations

**Components**:
- `IconRegistry` with simple geometric shapes
- Building extraction in `DataTransformer`
- Entity extraction (duplicants, critters)
- Icon overlay rendering in `StaticRenderer`
- CLI flags: `--show-buildings`, `--show-entities`

**Acceptance Criteria**:
- Buildings appear as icons at correct positions
- Duplicants/critters shown with distinct icons
- Icons scale appropriately with `--scale` parameter
- Can toggle icons on/off via CLI

### Phase 4: Polish & Game Assets
**Goal**: Production-quality renders matching in-game appearance

**Components**:
- `GameAssetLoader` reads actual ONI installation files
- Extract real element colors from game data
- Improve visual effects for liquid/gas states
- Better icon shapes/colors for building types
- Add `--scale` parameter validation and optimization
- Add `--show-grid` for coordinate reference

**Acceptance Criteria**:
- Renders closely match in-game appearance when game path provided
- Liquid/gas elements visually distinct from solids
- Grid overlay option available
- Comprehensive error handling and user feedback

### Phase 5: Comparison Tools (Future)
**Goal**: Support colony evolution tracking

**Components**:
- Diff mode: highlight changes between two saves
- Timelapse: generate sequence of images across saves
- Side-by-side comparison output

### Phase 6: Interactive HTML (Future)
**Goal**: Rich exploration experience in browser

**Components**:
- `InteractiveRenderer` implementation
- HTML Canvas-based rendering
- JavaScript for zoom, pan, tooltips
- Tile/building inspection on click/hover
- Layer toggles (buildings, entities, overlays)
- Multi-asteroid navigation

## Dependencies

### Python Libraries
- `Pillow` (PIL): Image rendering and manipulation
- Existing `oni_save_parser` library: Save file parsing
- Standard library: `pathlib`, `argparse`, `logging`, `json`

### Optional
- Game asset parsing (format TBD based on ONI data file structure)
- May need YAML parser if game data in YAML format

## Future Enhancements

### Additional Overlays
- Temperature heatmap
- Pressure/gas concentration
- Decor values
- Light levels
- Pathfinding/navigation overlay

### Advanced Features
- Configurable color schemes (colorblind-friendly palettes)
- Region/coordinate range selection
- Animation generation (gif/mp4 from save sequence)
- Integration with other analysis tools in this project

### Performance Optimizations
- Parallel asteroid rendering
- Incremental rendering for interactive mode
- Caching of frequently-used assets
- GPU acceleration for large maps (future consideration)

## Open Questions

1. **Game asset format**: Need to investigate actual format of ONI element definitions
   - Likely YAML or JSON
   - May need to reverse-engineer from game files
   - Fallback colors sufficient for MVP

2. **Icon design**: Should we extract actual game sprites or use custom icons?
   - Phase 3: Simple geometric shapes
   - Phase 4+: Consider sprite extraction if feasible
   - Legal considerations for redistributing game assets

3. **Performance limits**: What's the practical limit for map size?
   - Test with largest possible DLC configurations
   - May need progress indicators for slow renders
   - Consider multi-threading for asteroid rendering

## Success Metrics

- [ ] Can render terrain from any save file (with or without game assets)
- [ ] Renders are visually accurate compared to in-game view
- [ ] Multi-asteroid DLC saves handled correctly
- [ ] Building and entity icons clearly visible and positioned correctly
- [ ] CLI is intuitive and well-documented
- [ ] Test coverage >80% for core rendering logic
- [ ] Can generate comparison images for colony evolution analysis
- [ ] Performance: <10 seconds to render typical save file

## Conclusion

This design provides a solid foundation for ONI save file map rendering with a flexible pipeline architecture that supports incremental development. The phased approach allows delivery of a working MVP (terrain-only rendering) quickly, with clear paths to add buildings, entities, and eventually interactive HTML visualization.

The separation of concerns through the pipeline stages ensures testability and maintainability, while the separate-image-per-asteroid approach simplifies layout complexity and enables parallel rendering in the future.
