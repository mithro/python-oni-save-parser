"""Count resources in ONI save files.

This script analyzes storage containers, loose debris, and duplicant inventories
to provide a comprehensive inventory of all resources in your colony.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from oni_save_parser import load_save_file


def find_storage_containers(save: Any) -> list[dict[str, Any]]:
    """Find all storage containers in save file."""
    storage_prefabs = ["StorageLocker", "LiquidReservoir", "GasReservoir"]
    containers = []

    for group in save.game_objects:
        if group.prefab_name in storage_prefabs:
            for obj in group.objects:
                # Look for PrimaryElement to get mass data
                for behavior in obj.behaviors:
                    if behavior.name == "PrimaryElement":
                        mass = behavior.template_data.get("Mass", 0.0)
                        if mass > 0:
                            containers.append({
                                "prefab": group.prefab_name,
                                "mass": mass,
                                "position": (obj.position.x, obj.position.y)
                            })
    return containers


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files by location and element type"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        save = load_save_file(args.save_file)
        containers = find_storage_containers(save)

        print(f"Found {len(containers)} storage containers")
        for container in containers:
            print(f"  {container['prefab']}: {container['mass']:.1f} kg at {container['position']}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
