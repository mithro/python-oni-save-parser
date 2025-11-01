"""Fallback color palette for ONI elements when game assets unavailable."""

# RGB color tuples for common ONI elements
FALLBACK_COLORS: dict[str, tuple[int, int, int]] = {
    # Gases
    "Oxygen": (161, 219, 251),
    "CarbonDioxide": (88, 88, 88),
    "Hydrogen": (249, 226, 226),
    "ChlorineGas": (205, 255, 155),
    "Steam": (220, 220, 220),

    # Liquids
    "Water": (44, 111, 209),
    "DirtyWater": (115, 103, 82),
    "SaltWater": (93, 151, 185),
    "Brine": (162, 130, 101),
    "CrudeOil": (67, 47, 45),
    "Petroleum": (50, 39, 40),

    # Solids - Basic
    "Vacuum": (0, 0, 0),
    "Dirt": (115, 86, 58),
    "Sand": (192, 167, 106),
    "Clay": (146, 108, 82),
    "Granite": (124, 124, 124),
    "SandStone": (145, 117, 69),
    "Algae": (87, 152, 50),
    "Ice": (175, 218, 245),

    # Solids - Metals
    "IronOre": (170, 98, 65),
    "Copper": (184, 115, 51),
    "GoldAmalgam": (237, 201, 81),
    "Wolframite": (71, 71, 71),

    # Solids - Special
    "Phosphorite": (253, 222, 108),
    "Coal": (39, 39, 39),
    "Fertilizer": (158, 135, 98),
    "BleachStone": (255, 215, 180),
}

# Magenta for unknown elements (highly visible)
UNKNOWN_COLOR: tuple[int, int, int] = (255, 0, 255)


def get_fallback_color(element: str) -> tuple[int, int, int]:
    """
    Get fallback color for an element.

    Args:
        element: Element name/ID

    Returns:
        RGB color tuple (r, g, b) where each component is 0-255
    """
    return FALLBACK_COLORS.get(element, UNKNOWN_COLOR)
