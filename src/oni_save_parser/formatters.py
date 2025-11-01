"""Output formatting functions for ONI save game data.

This module provides formatters for different output modes:
- compact: Essential information for quick scanning
- detailed: Organized sections with full statistics
- json: Machine-readable for automation
"""

from typing import Any


def format_duplicant_compact(duplicant_data: dict[str, Any]) -> str:
    """Format duplicant data in compact mode.

    Args:
        duplicant_data: Dictionary with duplicant information

    Returns:
        Formatted string with essential duplicant info
    """
    lines = []

    # Header
    name = duplicant_data.get("name", "Unknown")
    lines.append(f"=== Duplicant: {name} ===")

    # Gender
    gender = duplicant_data.get("gender", "Unknown")
    lines.append(f"Gender: {gender}")

    # Skills (show top 3 non-zero skills)
    skills = duplicant_data.get("skills", {})
    skill_list = [(name, level) for name, level in skills.items() if level > 0]
    skill_list.sort(key=lambda x: x[1], reverse=True)
    if skill_list:
        top_skills = skill_list[:3]
        skill_str = ", ".join([f"{name} +{level}" for name, level in top_skills])
        lines.append(f"Skills: {skill_str}")

    # Traits
    traits = duplicant_data.get("traits", [])
    if traits:
        # Convert camelCase to Title Case
        formatted_traits = []
        for trait in traits:
            # Simple camelCase split: insert space before capitals
            spaced = "".join([f" {c}" if c.isupper() else c for c in trait]).strip()
            formatted_traits.append(spaced)
        traits_str = ", ".join(formatted_traits)
        lines.append(f"Traits: {traits_str}")

    # Health and Stress
    health = duplicant_data.get("health", {})
    stress = duplicant_data.get("stress", {})
    if health:
        health_current = int(health.get("current", 0))
        health_max = int(health.get("max", 100))
        stress_current = int(stress.get("current", 0))
        stress_percent = int((stress_current / stress.get("max", 100)) * 100)
        lines.append(f"Health: {health_current}/{health_max}  Stress: {stress_percent}%")

    # Position
    position = duplicant_data.get("position")
    if position:
        lines.append(f"Position: ({position[0]:.1f}, {position[1]:.1f})")

    return "\n".join(lines)


def format_geyser_compact(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    temperature_c: float,
    stats: dict[str, Any],
) -> str:
    """Format geyser information in compact one-line format.

    Args:
        prefab_name: Geyser type name
        index: Geyser index (0-based)
        position: (x, y) coordinates
        element: Element type (e.g., "Steam", "Natural Gas")
        temperature_c: Output temperature in Celsius
        stats: Statistics from extract_geyser_stats

    Returns:
        Formatted one-line string
    """
    avg_output = stats["average_output_lifetime_kg_s"]
    eruption_percent = stats["eruption_uptime_percent"]
    active_percent = stats["active_uptime_percent"]

    return (
        f"{prefab_name} #{index + 1}: {avg_output:.1f} kg/s avg @ "
        f"({position[0]}, {position[1]}) | "
        f"{eruption_percent:.0f}% erupting, {active_percent:.0f}% active | "
        f"{temperature_c:.1f}°C {element}"
    )
