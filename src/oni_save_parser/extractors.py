"""Data extraction functions for ONI save game objects.

This module provides reusable functions to extract gameplay-relevant
information from ONI save file game object behaviors.
"""

from typing import Any


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
    mastery_by_skill = {}
    if isinstance(mastery_raw, list):
        for item in mastery_raw:
            if isinstance(item, tuple) and len(item) == 2:
                skill_name, has_skill = item
                if has_skill:
                    # Extract skill level from name (e.g., "Mining3" -> level 3)
                    import re
                    match = re.search(r'(\D+)(\d+)', skill_name)
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
        "current_role": template_data.get("currentRole", "None")
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
    trait_ids = template_data.get("TraitIds", [])
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
        "can_be_incapacitated": template_data.get("CanBeIncapacitated", True)
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

        attributes[attr_id] = {
            "current": current,
            "max": max_val
        }

    return attributes
