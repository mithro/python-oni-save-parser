"""Data extraction functions for ONI save game objects.

This module provides reusable functions to extract gameplay-relevant
information from ONI save file game object behaviors.
"""

import re
from typing import Any

# Temperature range constants for data validation
# These represent the typical gameplay range in ONI (not absolute physical limits)
MIN_GAME_TEMP_K = 200.0  # Below this is extremely cold (colder than liquid oxygen)
MAX_GAME_TEMP_K = 4500.0  # Above this exceeds even tungsten volcano temps

# Geyser configuration mapping: prefab_name -> (element_id, temperature_k)
# Temperature values from ONI Wiki (converted to Kelvin: °C + 273.15)
# Covers base game + Spaced Out DLC as of January 2025
GEYSER_CONFIG = {
    # Water/Liquid Geysers
    "GeyserGeneric_hot_water": ("Water", 368.15),  # 95°C
    "GeyserGeneric_slush_water": ("Brine", 263.15),  # -10°C
    "GeyserGeneric_filthy_water": ("DirtyWater", 303.15),  # 30°C
    "GeyserGeneric_salt_water": ("SaltWater", 368.15),  # 95°C
    "GeyserGeneric_slush_salt_water": ("Brine", 263.15),  # -10°C
    "GeyserGeneric_liquid_sulfur": ("LiquidSulfur", 438.35),  # 165.2°C
    # Gas Geysers/Vents
    "GeyserGeneric_steam": ("Steam", 383.15),  # 110°C (Cool Steam Vent)
    "GeyserGeneric_hot_steam": ("Steam", 773.15),  # 500°C (Steam Vent)
    "GeyserGeneric_hot_co2": ("CarbonDioxide", 773.15),  # 500°C
    "GeyserGeneric_liquid_co2": ("LiquidCarbonDioxide", 218.0),  # -55.15°C
    "GeyserGeneric_hot_hydrogen": ("Hydrogen", 773.15),  # 500°C
    "GeyserGeneric_hot_po2": ("ContaminatedOxygen", 773.15),  # 500°C
    "GeyserGeneric_slimy_po2": ("ContaminatedOxygen", 333.15),  # 60°C
    "GeyserGeneric_methane": ("Methane", 423.15),  # 150°C
    "GeyserGeneric_chlorine_gas": ("ChlorineGas", 333.15),  # 60°C
    "GeyserGeneric_chlorine_gas_cool": ("ChlorineGas", 278.15),  # 5°C
    # Metal Volcanoes
    "GeyserGeneric_molten_copper": ("MoltenCopper", 2500.0),  # 2226.85°C
    "GeyserGeneric_molten_iron": ("MoltenIron", 2800.0),  # 2526.85°C
    "GeyserGeneric_molten_gold": ("MoltenGold", 2900.0),  # 2626.85°C
    "GeyserGeneric_molten_aluminum": ("MoltenAluminum", 2000.0),  # 1726.85°C
    "GeyserGeneric_molten_tungsten": ("MoltenTungsten", 4000.0),  # 3726.85°C
    "GeyserGeneric_molten_cobalt": ("MoltenCobalt", 2500.0),  # 2226.85°C
    "GeyserGeneric_molten_niobium": ("MoltenNiobium", 3500.0),  # 3226.85°C
    # Magma Volcanoes
    "GeyserGeneric_big_volcano": ("Magma", 2000.0),  # 1726.85°C (Major Volcano)
    "GeyserGeneric_small_volcano": ("Magma", 2000.0),  # 1726.85°C (Minor Volcano)
    # Other
    "OilWell": ("CrudeOil", 600.0),  # 326.85°C (Leaky Oil Fissure)
}


def get_geyser_config_from_prefab(prefab_name: str) -> tuple[str | None, float | None]:
    """Get default element ID and temperature for a geyser prefab.

    Args:
        prefab_name: Geyser prefab name (e.g., "GeyserGeneric_hot_water")

    Returns:
        Tuple of (element_id, temperature_k) or (None, None) if unknown

    Examples:
        get_geyser_config_from_prefab("GeyserGeneric_hot_water")
        # Returns: ('Water', 368.15)

        get_geyser_config_from_prefab("GeyserGeneric_chlorine_gas")
        # Returns: ('ChlorineGas', 333.15)

        get_geyser_config_from_prefab("UnknownGeyser")
        # Returns: (None, None)
    """
    config = GEYSER_CONFIG.get(prefab_name)
    if config:
        return config
    return (None, None)


def extract_duplicant_skills(minion_resume_behavior: Any) -> dict[str, Any]:
    """Extract skill levels from MinionResume behavior.

    Args:
        minion_resume_behavior: MinionResume behavior from duplicant object

    Returns:
        Dictionary with skill information:
        {
            'mastery_by_skill': Dict[str, int],  # Skill name -> level
            'aptitude_by_group': Dict[str, int],  # Skill group -> aptitude
            'current_role': str  # Current job role
        }
    """
    template_data = minion_resume_behavior.template_data or {}

    # MasteryBySkillID is a list of tuples like [('Mining1', True), ('Mining2', True)]
    # Convert to dict with skill levels extracted from number suffix
    mastery_raw = template_data.get("MasteryBySkillID", [])
    mastery_by_skill: dict[str, int] = {}
    if isinstance(mastery_raw, list):
        for item in mastery_raw:
            if isinstance(item, tuple) and len(item) == 2:
                skill_name, has_skill = item
                if has_skill:
                    # Extract skill level from name (e.g., "Mining3" -> level 3)
                    match = re.search(r"(\D+)(\d+)", skill_name)
                    if match:
                        base_name = match.group(1)
                        level = int(match.group(2))
                        # Keep highest level for each skill
                        mastery_by_skill[base_name] = max(mastery_by_skill.get(base_name, 0), level)
    elif isinstance(mastery_raw, dict):
        mastery_by_skill = mastery_raw

    return {
        "mastery_by_skill": mastery_by_skill,
        "aptitude_by_group": template_data.get("AptitudeBySkillGroup", {}),
        "current_role": template_data.get("currentRole", "None"),
    }


def extract_duplicant_traits(traits_behavior: Any) -> list[str]:
    """Extract personality traits from Klei.AI.Traits behavior.

    Args:
        traits_behavior: Klei.AI.Traits behavior from duplicant object

    Returns:
        List of trait names: ['QuickLearner', 'Yokel', 'MouthBreather']
    """
    template_data = traits_behavior.template_data or {}

    # Try TraitIds first (used in actual save files)
    trait_ids: list[str] = template_data.get("TraitIds", [])
    if trait_ids:
        return trait_ids

    # Fall back to TraitList for older format or tests
    trait_list = template_data.get("TraitList", [])
    trait_names = []
    for trait in trait_list:
        if hasattr(trait, "Name"):
            trait_names.append(trait.Name)
        elif isinstance(trait, dict):
            trait_names.append(trait.get("Name", "Unknown"))

    return trait_names


def extract_health_status(health_behavior: Any) -> dict[str, Any]:
    """Extract health and status information from Health behavior.

    Args:
        health_behavior: Health behavior from duplicant object

    Returns:
        Dictionary with health status:
        {
            'state': str,  # 'Alive', 'Incapacitated', 'Dead'
            'can_be_incapacitated': bool
        }
    """
    template_data = health_behavior.template_data or {}

    # State enum: 0=Alive, 1=Incapacitated, 2=Dead
    state_map = {0: "Alive", 1: "Incapacitated", 2: "Dead"}
    state_value = template_data.get("State", 0)

    return {
        "state": state_map.get(state_value, "Unknown"),
        "can_be_incapacitated": template_data.get("CanBeIncapacitated", True),
    }


def extract_attribute_levels(attribute_levels_behavior: Any) -> dict[str, dict[str, float]]:
    """Extract current attribute levels (health, stress, etc.).

    Args:
        attribute_levels_behavior: Klei.AI.AttributeLevels behavior

    Returns:
        Dictionary mapping attribute names to current/max values:
        {
            'HitPoints': {'current': 85.0, 'max': 100.0},
            'Stress': {'current': 12.0, 'max': 100.0},
            ...
        }
    """
    template_data = attribute_levels_behavior.template_data or {}
    save_load_levels = template_data.get("saveLoadLevels", [])

    attributes = {}
    for attr in save_load_levels:
        if hasattr(attr, "AttributeId"):
            attr_id = attr.AttributeId
            current = getattr(attr, "experience", 0.0)
            max_val = getattr(attr, "experienceMax", 100.0)
        elif isinstance(attr, dict):
            # Handle lowercase field names (actual save file format)
            attr_id = attr.get("attributeId") or attr.get("AttributeId", "Unknown")
            current = attr.get("experience", 0.0)
            # Calculate max from level (each level is 100 experience)
            level = attr.get("level", 0)
            max_val = (level + 1) * 100.0 if level >= 0 else 100.0
        else:
            continue

        attributes[attr_id] = {"current": current, "max": max_val}

    return attributes


def extract_geyser_stats(
    config: dict[str, Any],
    element_data: dict[str, Any] | None = None,
    temperature_k: float | None = None,
) -> dict[str, Any]:
    """Extract gameplay statistics from geyser configuration.

    Args:
        config: Geyser configuration dictionary from behavior template_data
        element_data: Optional element properties (for thermal calculations)
        temperature_k: Optional output temperature in Kelvin

    Returns:
        Dictionary with calculated geyser statistics:
        {
            # Rates
            'emission_rate_kg_s': float,           # Peak emission rate (kg/s)
            'average_output_active_kg_s': float,   # Average during active periods (kg/s)
            'average_output_lifetime_kg_s': float, # Average over entire lifetime (kg/s)

            # Eruption cycle
            'eruption_duration_s': float,          # Length of each eruption (seconds)
            'idle_duration_s': float,              # Idle period between eruptions (seconds)
            'eruption_cycle_s': float,             # Total eruption cycle length (seconds)
            'eruption_uptime_percent': float,      # Percentage of eruption cycle spent erupting

            # Dormancy cycle
            'active_duration_s': float,            # Length of active period (seconds)
            'dormant_duration_s': float,           # Length of dormant period (seconds)
            'dormancy_cycle_s': float,             # Total dormancy cycle length (seconds)
            'active_uptime_percent': float,        # Percentage of dormancy cycle spent active

            # Overall
            'overall_uptime_percent': float,       # Combined eruption and active uptime percentage

            # Production
            'kg_per_eruption': float,              # Total kg produced per single eruption
            'kg_per_eruption_cycle': float,        # Total kg produced per eruption cycle
            'kg_per_active_period': float,         # Total kg produced per active period

            # Storage
            'storage_for_idle_kg': float,          # Storage needed for idle periods (kg)
            'storage_for_dormancy_kg': float,      # Storage needed for dormancy periods (kg)
            'recommended_storage_kg': float,       # Recommended storage capacity (kg)
        }
    """
    # Extract raw values
    emission_rate = config.get("scaledRate", 0.0)
    iteration_length = config.get("scaledIterationLength", 0.0)
    iteration_percent = config.get("scaledIterationPercent", 0.0)
    year_length = config.get("scaledYearLength", 0.0)
    year_percent = config.get("scaledYearPercent", 0.0)

    # Calculate rates
    avg_active = emission_rate * iteration_percent
    avg_lifetime = emission_rate * iteration_percent * year_percent

    # Calculate durations
    eruption_duration = iteration_length * iteration_percent
    idle_duration = iteration_length * (1 - iteration_percent)
    active_duration = year_length * year_percent
    dormant_duration = year_length * (1 - year_percent)

    # Calculate percentages
    eruption_uptime_percent = iteration_percent * 100
    active_uptime_percent = year_percent * 100
    overall_uptime_percent = iteration_percent * year_percent * 100

    # Calculate production amounts
    kg_per_eruption = emission_rate * eruption_duration
    kg_per_eruption_cycle = avg_active * iteration_length
    kg_per_active_period = avg_active * active_duration

    # Calculate storage requirements
    storage_idle = avg_active * idle_duration
    storage_dormancy = avg_lifetime * dormant_duration
    recommended_storage = max(storage_idle, storage_dormancy)

    result = {
        # Rates
        "emission_rate_kg_s": emission_rate,
        "average_output_active_kg_s": avg_active,
        "average_output_lifetime_kg_s": avg_lifetime,
        # Eruption cycle
        "eruption_duration_s": eruption_duration,
        "idle_duration_s": idle_duration,
        "eruption_cycle_s": iteration_length,
        "eruption_uptime_percent": eruption_uptime_percent,
        # Dormancy cycle
        "active_duration_s": active_duration,
        "dormant_duration_s": dormant_duration,
        "dormancy_cycle_s": year_length,
        "active_uptime_percent": active_uptime_percent,
        # Overall
        "overall_uptime_percent": overall_uptime_percent,
        # Production amounts
        "kg_per_eruption": kg_per_eruption,
        "kg_per_eruption_cycle": kg_per_eruption_cycle,
        "kg_per_active_period": kg_per_active_period,
        # Storage requirements
        "storage_for_idle_kg": storage_idle,
        "storage_for_dormancy_kg": storage_dormancy,
        "recommended_storage_kg": recommended_storage,
    }

    # Add thermal calculations if data available
    if element_data and temperature_k:
        shc = element_data.get("specific_heat_capacity")
        if shc:
            # DTU = kg * SHC * temperature, convert to kDTU by dividing by 1000
            peak_thermal = emission_rate * shc * temperature_k / 1000
            avg_thermal = avg_lifetime * shc * temperature_k / 1000
            thermal_per_eruption = kg_per_eruption * shc * temperature_k / 1000

            result.update(
                {
                    "peak_thermal_power_kdtu_s": peak_thermal,
                    "average_thermal_power_kdtu_s": avg_thermal,
                    "thermal_per_eruption_kdtu": thermal_per_eruption,
                }
            )

    return result
