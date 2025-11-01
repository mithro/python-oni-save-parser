"""Pipeline orchestrator for map rendering."""
from pathlib import Path

from oni_save_parser import load_save_file
from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.models import AsteroidData, SaveMetadata
from oni_save_parser.rendering.static_renderer import StaticRenderer
from oni_save_parser.rendering.transformers import DataTransformer


class MapRenderer:
    """Orchestrates the map rendering pipeline."""

    def __init__(self) -> None:
        """Initialize the renderer pipeline."""
        # Phase 1: No game assets, use fallback colors only
        self.element_registry = ElementRegistry()
        self.transformer = DataTransformer(self.element_registry)

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
        save_path = Path(save_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Parse
        save_data = load_save_file(save_path)

        # Stage 2: Transform
        world_model = self.transformer.transform(save_data)

        # Stage 3: Render each asteroid
        renderer = StaticRenderer(self.element_registry, scale=scale)
        output_files = []

        for asteroid in world_model.asteroids:
            # Build output filename
            output_path = self._build_output_path(
                output_dir,
                world_model.metadata,
                asteroid,
            )

            # Render
            renderer.render_asteroid(asteroid, output_path)
            output_files.append(str(output_path))

        return output_files

    def _build_output_path(
        self,
        output_dir: Path,
        metadata: SaveMetadata,
        asteroid: AsteroidData,
    ) -> Path:
        """Build output filename for an asteroid."""
        # Sanitize colony name
        colony_name = metadata.colony_name.replace(" ", "-")

        filename = (
            f"{colony_name}_"
            f"cycle-{metadata.cycle_number}_"
            f"asteroid-{asteroid.id}-{asteroid.name}.png"
        )

        return output_dir / filename
