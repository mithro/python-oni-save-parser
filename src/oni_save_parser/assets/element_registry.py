"""Element registry for mapping element IDs to visual properties."""
from oni_save_parser.assets.fallback_colors import get_fallback_color


class ElementRegistry:
    """
    Maps element IDs to colors.

    Phase 1: Uses only fallback colors.
    Future: Load from game assets when available.
    """

    def __init__(self) -> None:
        """Initialize the registry with fallback colors."""
        # Future: Accept optional GameAssetLoader
        pass

    def get_color(self, element: str) -> tuple[int, int, int]:
        """
        Get RGB color for an element.

        Args:
            element: Element name/ID

        Returns:
            RGB tuple (r, g, b) where each component is 0-255
        """
        return get_fallback_color(element)
