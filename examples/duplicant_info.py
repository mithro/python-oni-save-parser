"""Extract and display duplicant information from ONI save files.

This script loads a save file and prints detailed information about duplicants
including their name, traits, skills, stress, health, and current activities.
"""

import argparse
import sys
from pathlib import Path

from oni_save_parser import get_game_objects_by_prefab, load_save_file


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

        print(f"Found {len(duplicants)} duplicants")

        for idx, dup in enumerate(duplicants, 1):
            print(f"\n=== Duplicant #{idx} ===")
            print(f"Position: ({dup.position.x:.1f}, {dup.position.y:.1f})")
            print(f"Behaviors: {len(dup.behaviors)}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
