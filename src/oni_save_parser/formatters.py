"""Output formatting functions for ONI save game data.

This module provides formatters for different output modes:
- compact: Essential information for quick scanning
- detailed: Organized sections with full statistics
- json: Machine-readable for automation
"""

import math
import re
from typing import Any

# ONI game constants
ONI_CYCLE_DURATION_SECONDS = 600.0  # 1 cycle = 600 seconds
GAS_RESERVOIR_CAPACITY_KG = 1000  # Gas Reservoir capacity
LIQUID_RESERVOIR_CAPACITY_KG = 5000  # Liquid Reservoir capacity


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
        formatted_traits = []
        for trait in traits:
            # Handle "Grant Skill_" traits specially
            if trait.startswith("GrantSkill_") or trait.startswith("Grant Skill_"):
                # Extract skill name after the prefix
                skill_part = trait.replace("GrantSkill_", "").replace("Grant Skill_", "").strip()
                # Split skill name and level (e.g., "Mining2" → "Mining 2")
                match = re.match(r"([A-Za-z]+)(\d+)", skill_part)
                if match:
                    skill_name = match.group(1)
                    skill_level = match.group(2)
                    formatted_traits.append(f"Grants Skill: {skill_name} {skill_level}")
                else:
                    formatted_traits.append(f"Grants Skill: {skill_part}")
            # Apply manual overrides for known trait names
            elif trait == "CantDig":
                formatted_traits.append("Can't Dig")
            elif trait == "CantBuild":
                formatted_traits.append("Can't Build")
            elif trait == "CantCook":
                formatted_traits.append("Can't Cook")
            elif trait == "CantResearch":
                formatted_traits.append("Can't Research")
            else:
                # Convert camelCase to Title Case: insert space before capitals
                spaced = "".join([f" {c}" if c.isupper() else c for c in trait]).strip()
                formatted_traits.append(spaced)

        if formatted_traits:
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
    avg_output = format_rate(stats["average_output_lifetime_kg_s"])
    eruption_percent = stats["eruption_uptime_percent"]
    active_percent = stats["active_uptime_percent"]

    return (
        f"{prefab_name} #{index + 1}: {avg_output} avg @ "
        f"({position[0]}, {position[1]}) | "
        f"{eruption_percent:.0f}% erupting, {active_percent:.0f}% active | "
        f"{temperature_c:.1f}°C {element}"
    )


def format_duration(seconds: float) -> str:
    """Format duration in seconds and cycles.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string with seconds and cycles
    """
    cycles = seconds / ONI_CYCLE_DURATION_SECONDS

    if cycles < 1.0:
        return f"{seconds:.1f}s ({cycles:.1f} cycles)"
    else:
        return f"{cycles:.1f} cycles ({seconds:,.1f}s)"


def format_mass(kg: float) -> str:
    """Format mass in kg or tons.

    Args:
        kg: Mass in kilograms

    Returns:
        Formatted string with appropriate unit
    """
    if kg >= 1000:
        return f"{kg / 1000:.1f} t"
    else:
        return f"{kg:.1f} kg"


def format_rate(kg_s: float) -> str:
    """Format mass flow rate in g/s or kg/s.

    Args:
        kg_s: Mass flow rate in kg/s

    Returns:
        Formatted string with appropriate unit (g/s for < 1 kg/s, kg/s for >= 1 kg/s)
    """
    if kg_s < 1.0:
        return f"{kg_s * 1000:.1f} g/s"
    else:
        return f"{kg_s:.1f} kg/s"


def format_geyser_detailed(
    prefab_name: str,
    index: int,
    position: tuple[float, float],
    element: str,
    element_state: str,
    temperature_c: float,
    stats: dict[str, Any],
    thermal_stats: dict[str, Any] | None = None,
    element_max_mass: float | None = None,
    analyzed: bool = True,
) -> str:
    """Format geyser information in detailed multi-line format.

    Args:
        prefab_name: Geyser type name
        index: Geyser index (0-based)
        position: (x, y) coordinates
        element: Element type
        element_state: "Gas" or "Liquid"
        temperature_c: Output temperature in Celsius
        stats: Statistics from extract_geyser_stats
        thermal_stats: Optional thermal statistics
        element_max_mass: Optional max kg per tile (for liquids)
        analyzed: Whether geyser has been analyzed (default True)

    Returns:
        Formatted multi-line string
    """
    lines = []

    # Header
    lines.append(f"=== {prefab_name} #{index + 1} ===")
    lines.append(f"Position:         ({position[0]}, {position[1]})")
    lines.append(f"Output Element:   {element} ({element_state})")
    lines.append(f"Output Temp:      {temperature_c:.1f}°C")
    lines.append(f"Analyzed:         {'Yes' if analyzed else 'No (estimated from prefab)'}")
    lines.append("")

    # Output Rates (use appropriate units: g/s for small, kg/s for large)
    lines.append("Output Rates:")
    lifetime_rate = format_rate(stats["average_output_lifetime_kg_s"])
    active_rate = format_rate(stats["average_output_active_kg_s"])
    peak_rate = format_rate(stats["emission_rate_kg_s"])
    lines.append(f"  Average (lifetime):        {lifetime_rate:>12}  (accounts for all downtime)")
    lines.append(f"  Average (when active):     {active_rate:>12}  (during active period only)")
    lines.append(f"  Peak (when erupting):      {peak_rate:>12}  (maximum output rate)")
    lines.append("")

    # Thermal Output (if available)
    if thermal_stats:
        peak_thermal = thermal_stats.get("peak_thermal_power_kdtu_s", 0)
        avg_thermal = thermal_stats.get("average_thermal_power_kdtu_s", 0)
        thermal_eruption = thermal_stats.get("thermal_per_eruption_kdtu", 0)

        lines.append("Thermal Output:")
        lines.append(f"  Peak thermal power:          {peak_thermal:>7.1f} kDTU/s  (when erupting)")
        lines.append(
            f"  Average thermal power:       {avg_thermal:>7.1f} kDTU/s  (lifetime average)"
        )
        eruption_dur_str = format_duration(stats["eruption_duration_s"])
        lines.append(
            f"  Total heat per eruption: {thermal_eruption:>11,.1f} kDTU    "
            f"(over {eruption_dur_str})"
        )
        lines.append("")

    # Eruption Cycle
    lines.append("Eruption Cycle (short-term):")

    erupting_dur = format_duration(stats["eruption_duration_s"])
    idle_dur = format_duration(stats["idle_duration_s"])
    cycle_dur = format_duration(stats["eruption_cycle_s"])

    kg_eruption_raw = stats["kg_per_eruption"]
    if kg_eruption_raw >= 1000:
        kg_eruption_str = f"{kg_eruption_raw / 1000:>7.1f} t"
    else:
        kg_eruption_str = f"{kg_eruption_raw:>7.1f} kg"

    thermal_eruption_str = ""
    if thermal_stats:
        thermal_value = thermal_stats.get("thermal_per_eruption_kdtu", 0)
        thermal_eruption_str = f" @ {thermal_value:>11,.0f} kDTU"

    lines.append(
        f"  Erupting:    {erupting_dur:>20}  → Produces {kg_eruption_str}{thermal_eruption_str}"
    )
    lines.append(f"  Idle:        {idle_dur:>20}  → Produces    0.0 kg")
    lines.append(f"  Total cycle: {cycle_dur:>20}")
    lines.append(f"  Uptime:      {stats['eruption_uptime_percent']:>6.1f}%")
    lines.append("")

    # Storage for idle
    storage_idle = format_mass(stats["storage_for_idle_kg"])
    lines.append(f"  Storage for idle period: {storage_idle}")

    # Calculate reservoir count
    if element_state == "Gas":
        reservoir_count = math.ceil(stats["storage_for_idle_kg"] / GAS_RESERVOIR_CAPACITY_KG)
        lines.append(
            f"    - {reservoir_count} Gas Reservoir"
            f"{'s' if reservoir_count != 1 else ''} (1,000 kg each)"
        )

    lines.append("")

    # Dormancy Cycle
    lines.append("Dormancy Cycle (long-term):")

    active_dur = format_duration(stats["active_duration_s"])
    dormant_dur = format_duration(stats["dormant_duration_s"])
    dormancy_cycle_dur = format_duration(stats["dormancy_cycle_s"])

    kg_active_raw = stats["kg_per_active_period"]
    if kg_active_raw >= 1000:
        kg_active_str = f"{kg_active_raw / 1000:>7.1f} t"
    else:
        kg_active_str = f"{kg_active_raw:>7.1f} kg"

    thermal_active_str = ""
    if thermal_stats and "thermal_per_eruption_kdtu" in thermal_stats:
        # Total thermal during active period
        if stats["eruption_cycle_s"] > 0:
            num_eruptions = stats["active_duration_s"] / stats["eruption_cycle_s"]
            total_thermal_active = thermal_stats["thermal_per_eruption_kdtu"] * num_eruptions
            thermal_active_str = f" @ {total_thermal_active:>11,.0f} kDTU"

    lines.append(f"  Active:      {active_dur:>28}  → Produces {kg_active_str}{thermal_active_str}")
    lines.append(f"  Dormant:     {dormant_dur:>28}  → Produces    0.0 kg")
    lines.append(f"  Total cycle: {dormancy_cycle_dur:>28}")
    lines.append(f"  Uptime:      {stats['active_uptime_percent']:>6.1f}%")
    lines.append("")

    # Storage for dormancy
    storage_dormancy = format_mass(stats["storage_for_dormancy_kg"])
    lines.append(f"  Storage for dormancy: {storage_dormancy}")

    # Calculate reservoir and tile storage
    if element_state == "Gas":
        reservoir_count = math.ceil(stats["storage_for_dormancy_kg"] / GAS_RESERVOIR_CAPACITY_KG)
        lines.append(
            f"    - {reservoir_count} Gas Reservoir"
            f"{'s' if reservoir_count != 1 else ''} (1,000 kg each)"
        )
    else:  # Liquid
        reservoir_count = math.ceil(stats["storage_for_dormancy_kg"] / LIQUID_RESERVOIR_CAPACITY_KG)
        lines.append(
            f"    - {reservoir_count} Liquid Reservoir"
            f"{'s' if reservoir_count != 1 else ''} (5,000 kg each)"
        )
        if element_max_mass:
            tile_count = math.ceil(stats["storage_for_dormancy_kg"] / element_max_mass)
            lines.append(f"    - {tile_count} tiles @ {element_max_mass:,.0f} kg/tile max")

    lines.append("")

    # Overall summary
    lines.append(
        f"Overall Uptime: {stats['overall_uptime_percent']:.1f}% "
        f"({stats['eruption_uptime_percent']:.1f}% erupting × "
        f"{stats['active_uptime_percent']:.1f}% active)"
    )
    lines.append("")

    # Recommended storage
    recommended = format_mass(stats["recommended_storage_kg"])
    buffer_type = (
        "dormancy" if stats["storage_for_dormancy_kg"] > stats["storage_for_idle_kg"] else "idle"
    )
    lines.append(f"Recommended minimum storage: {recommended} ({buffer_type} buffer dominates)")

    return "\n".join(lines)
