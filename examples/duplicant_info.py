"""Extract and display duplicant information from ONI save files.

This script loads a save file and prints detailed information about duplicants
including their name, traits, skills, stress, health, and current activities.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from oni_save_parser import get_game_objects_by_prefab, load_save_file
from oni_save_parser.extractors import (
    extract_attribute_levels,
    extract_duplicant_skills,
    extract_duplicant_traits,
    extract_health_status,
)
from oni_save_parser.formatters import format_duplicant_compact


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
        "skills": {},
        "traits": [],
        "health": {},
        "stress": {},
        "behaviors": [],
    }

    # Extract data from behaviors
    for behavior in dup_object.behaviors:
        info["behaviors"].append(behavior.name)

        if behavior.name == "MinionIdentity" and behavior.template_data:
            info["name"] = behavior.template_data.get("name", "Unknown")
            info["gender"] = behavior.template_data.get("gender", "Unknown")

        elif behavior.name == "MinionResume":
            skills_data = extract_duplicant_skills(behavior)
            info["skills"] = skills_data.get("mastery_by_skill", {})

        elif behavior.name == "Klei.AI.Traits":
            info["traits"] = extract_duplicant_traits(behavior)

        elif behavior.name == "Health":
            health_data = extract_health_status(behavior)
            info["health_state"] = health_data.get("state", "Unknown")

        elif behavior.name == "Klei.AI.AttributeLevels":
            attrs = extract_attribute_levels(behavior)
            info["health"] = attrs.get("HitPoints", {})
            info["stress"] = attrs.get("Stress", {})

    return info


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument(
        "--format",
        choices=["compact", "detailed", "json"],
        default="compact",
        help="Output format (default: compact)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show internal behavior lists"
    )

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Load save and get duplicants
        save = load_save_file(args.save_file)
        duplicants = get_game_objects_by_prefab(save, "Minion")

        # Extract info for all duplicants
        dup_info_list = [extract_duplicant_info(dup) for dup in duplicants]

        if args.format == "json":
            # Remove behaviors from JSON output unless debug mode
            if not args.debug:
                for info in dup_info_list:
                    info.pop("behaviors", None)
            print(json.dumps(dup_info_list, indent=2, default=str))

        elif args.format == "compact":
            print(f"Found {len(duplicants)} duplicants\n")
            for info in dup_info_list:
                print(format_duplicant_compact(info))

                # Show behaviors in debug mode
                if args.debug:
                    print(f"\nDEBUG - Behaviors: {', '.join(info['behaviors'])}")
                print()

        else:  # detailed format - not implemented yet
            print("Detailed format not yet implemented", file=sys.stderr)
            return 1

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
