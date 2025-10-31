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

    return {
        "mastery_by_skill": template_data.get("MasteryBySkillID", {}),
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
    trait_list = template_data.get("TraitList", [])

    # Extract trait names from trait objects
    trait_names = []
    for trait in trait_list:
        if hasattr(trait, "Name"):
            trait_names.append(trait.Name)
        elif isinstance(trait, dict):
            trait_names.append(trait.get("Name", "Unknown"))

    return trait_names
