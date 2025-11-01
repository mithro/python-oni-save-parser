"""Static PNG renderer for ONI save files."""
from pathlib import Path

from PIL import Image

from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.cell_renderer import CellRenderer
from oni_save_parser.rendering.models import AsteroidData


class StaticRenderer:
    """Renders asteroids to static PNG images."""

    def __init__(self, element_registry: ElementRegistry, scale: int = 2) -> None:
        """
        Initialize renderer.

        Args:
            element_registry: Registry for element colors
            scale: Pixels per tile (1-10)
        """
        self.element_registry = element_registry
        self.scale = max(1, min(10, scale))  # Clamp to 1-10
        self.cell_renderer = CellRenderer(element_registry)

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
        # Calculate output dimensions
        width = asteroid.width * self.scale
        height = asteroid.height * self.scale

        # Create image
        img = Image.new("RGB", (width, height))
        pixels = img.load()

        # Render each cell
        for y in range(asteroid.height):
            for x in range(asteroid.width):
                cell = asteroid.cells[y][x]
                color = self.cell_renderer.render_cell(cell)

                # Fill scaled tile
                for dy in range(self.scale):
                    for dx in range(self.scale):
                        px = x * self.scale + dx
                        py = y * self.scale + dy
                        pixels[px, py] = color

        # Save image
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path)
