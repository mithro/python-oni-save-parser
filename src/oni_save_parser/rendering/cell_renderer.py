"""Cell renderer for converting cells to colors."""
from oni_save_parser.assets.element_registry import ElementRegistry
from oni_save_parser.rendering.models import Cell, ElementState


class CellRenderer:
    """Renders individual cells to RGB colors."""

    def __init__(self, element_registry: ElementRegistry) -> None:
        """
        Initialize renderer.

        Args:
            element_registry: Registry for element colors
        """
        self.element_registry = element_registry

    def render_cell(self, cell: Cell) -> tuple[int, int, int]:
        """
        Render a cell to an RGB color.

        Args:
            cell: Cell to render

        Returns:
            RGB color tuple (r, g, b)
        """
        # Get base color from registry
        color = self.element_registry.get_color(cell.element)

        # Vacuum is always rendered as-is (black)
        if cell.element == "Vacuum":
            return color

        # Apply state-based visual effects
        if cell.state == ElementState.LIQUID:
            return self._apply_liquid_effect(color)
        elif cell.state == ElementState.GAS:
            return self._apply_gas_effect(color)
        else:  # SOLID
            return color

    def _apply_liquid_effect(self, color: tuple[int, int, int]) -> tuple[int, int, int]:
        """
        Apply visual effect for liquids (slight brightness boost).

        Args:
            color: Base RGB color

        Returns:
            Modified RGB color
        """
        r, g, b = color
        # Increase brightness by 10%
        factor = 1.1
        return (
            min(255, int(r * factor)),
            min(255, int(g * factor)),
            min(255, int(b * factor)),
        )

    def _apply_gas_effect(self, color: tuple[int, int, int]) -> tuple[int, int, int]:
        """
        Apply visual effect for gases (lighter appearance).

        Args:
            color: Base RGB color

        Returns:
            Modified RGB color
        """
        r, g, b = color
        # Lighten by blending with white (60% original, 40% white)
        factor = 0.6
        return (
            int(r * factor + 255 * (1 - factor)),
            int(g * factor + 255 * (1 - factor)),
            int(b * factor + 255 * (1 - factor)),
        )
