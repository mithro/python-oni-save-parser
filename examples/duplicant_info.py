"""Extract and display duplicant information from ONI save files.

This script loads a save file and prints detailed information about duplicants
including their name, traits, skills, stress, health, and current activities.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from oni_save_parser import get_game_objects_by_prefab, load_save_file


def extract_duplicant_info(dup_object: Any) -> dict[str, Any]:
    """Extract information from a duplicant game object.

    Args:
        dup_object: GameObject representing a duplicant

    Returns:
        Dictionary with duplicant information
    """
    info: dict[str, Any] = {
        "position": (dup_object.position.x, dup_object.position.y),
        "name": "Unknown",
        "gender": "Unknown",
        "personality": "Unknown",
        "voice_pitch": 1.0,
        "behaviors": [],
    }

    # Extract data from behaviors
    for behavior in dup_object.behaviors:
        info["behaviors"].append(behavior.name)

        if behavior.name == "MinionIdentity" and behavior.template_data:
            info["name"] = behavior.template_data.get("name", "Unknown")
            info["gender"] = behavior.template_data.get("gender", "Unknown")
            info["personality"] = behavior.template_data.get("personalityResourceId", "Unknown")
            info["voice_pitch"] = behavior.template_data.get("voicePitch", 1.0)

    return info


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Load save and get duplicants
        save = load_save_file(args.save_file)
        duplicants = get_game_objects_by_prefab(save, "Minion")

        print(f"Found {len(duplicants)} duplicants\n")

        for idx, dup in enumerate(duplicants, 1):
            info = extract_duplicant_info(dup)

            print(f"=== Duplicant #{idx}: {info['name']} ===")
            print(f"Gender: {info['gender']}")
            print(f"Personality: {info['personality'].replace('DUPLICANT_PERSONALITY_', '')}")
            print(f"Position: ({info['position'][0]:.1f}, {info['position'][1]:.1f})")
            print(f"Behaviors: {', '.join(info['behaviors'])}")
            print()

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
