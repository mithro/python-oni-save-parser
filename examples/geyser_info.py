"""Extract and display geyser information from ONI save files.

This script loads a save file and prints detailed information about all geysers,
including their type, state, emission rates, and dormancy cycles.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from oni_save_parser import load_save_file, get_game_objects_by_prefab, list_prefab_types
from oni_save_parser.element_loader import get_global_element_loader


def find_geyser_prefabs(save_file_path: Path) -> list[str]:
    """Find all prefab types that are geysers.

    Args:
        save_file_path: Path to save file

    Returns:
        List of geyser prefab names
    """
    save = load_save_file(save_file_path)
    all_prefabs = list_prefab_types(save)

    # Geysers typically have "Geyser" in their name
    geyser_prefabs = [p for p in all_prefabs if "geyser" in p.lower() or "vent" in p.lower()]

    return geyser_prefabs


def extract_geyser_info(geyser_object: Any) -> dict[str, Any]:
    """Extract information from a geyser game object.

    Args:
        geyser_object: GameObject representing a geyser

    Returns:
        Dictionary with geyser information
    """
    info: dict[str, Any] = {
        "position": f"({geyser_object.position.x:.1f}, {geyser_object.position.y:.1f})",
        "behaviors": [],
    }

    # Extract data from behaviors
    for behavior in geyser_object.behaviors:
        if behavior.name == "Geyser":
            # Main geyser component with state
            if behavior.template_data:
                info["geyser_state"] = behavior.template_data
        elif behavior.name == "ElementEmitter":
            # Element emission info
            if behavior.template_data:
                info["emission"] = behavior.template_data
        elif behavior.name == "Discoverable":
            # Discovery state
            if behavior.template_data:
                info["discovered"] = behavior.template_data
        elif behavior.name == "Temperature":
            # Temperature info
            if behavior.template_data:
                info["temperature"] = behavior.template_data

        info["behaviors"].append(behavior.name)

    return info


def format_geyser_output(prefab_name: str, index: int, info: dict[str, Any], debug: bool = False) -> str:
    """Format geyser information for display.

    Args:
        prefab_name: Prefab type name
        index: Geyser index
        info: Geyser information dictionary
        debug: Whether to show behavior lists

    Returns:
        Formatted string
    """
    output = [f"\n=== {prefab_name} #{index + 1} ==="]
    output.append(f"Position: {info['position']}")

    # Only show behaviors in debug mode
    if debug:
        output.append(f"DEBUG - Behaviors: {', '.join(info['behaviors'])}")

    if "geyser_state" in info:
        output.append("\nGeyser State:")
        for key, value in info["geyser_state"].items():
            output.append(f"  {key}: {value}")

    if "emission" in info:
        output.append("\nEmission:")
        for key, value in info["emission"].items():
            output.append(f"  {key}: {value}")

    if "temperature" in info:
        output.append(f"\nTemperature: {info['temperature']}")

    if "discovered" in info:
        discovered = info["discovered"].get("discovered", False)
        output.append(f"\nDiscovered: {discovered}")

    return "\n".join(output)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract geyser information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")
    parser.add_argument(
        "--list-prefabs",
        action="store_true",
        help="Just list geyser prefab types and exit",
    )
    parser.add_argument(
        "--prefab",
        type=str,
        help="Only show geysers of this prefab type",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show internal behavior lists",
    )
    parser.add_argument(
        "--skip-vents",
        action="store_true",
        help="Only show actual geysers, not vents",
    )

    args = parser.parse_args()

    # Initialize element loader
    element_loader = get_global_element_loader()
    if element_loader is None and not args.debug:
        print("Warning: Could not find ONI element data. Thermal calculations unavailable.", file=sys.stderr)

    if not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        # Find geyser prefabs
        geyser_prefabs = find_geyser_prefabs(args.save_file)

        if not geyser_prefabs:
            print("No geysers found in save file.")
            return 0

        # Filter out vents if --skip-vents is set
        if args.skip_vents:
            geyser_prefabs = [p for p in geyser_prefabs if "vent" not in p.lower()]

        if args.list_prefabs:
            print("Geyser prefabs found:")
            for prefab in sorted(geyser_prefabs):
                print(f"  - {prefab}")
            return 0

        # Filter to specific prefab if requested
        if args.prefab:
            geyser_prefabs = [p for p in geyser_prefabs if p == args.prefab]
            if not geyser_prefabs:
                print(f"Error: Prefab '{args.prefab}' not found", file=sys.stderr)
                return 1

        # Load save and extract geyser info
        save = load_save_file(args.save_file)

        if args.json:
            import json

            all_geysers = {}
            for prefab in geyser_prefabs:
                objects = get_game_objects_by_prefab(save, prefab)
                all_geysers[prefab] = [extract_geyser_info(obj) for obj in objects]

            print(json.dumps(all_geysers, indent=2, default=str))
        else:
            # Text output
            total_count = 0
            for prefab in sorted(geyser_prefabs):
                objects = get_game_objects_by_prefab(save, prefab)
                if not objects:
                    continue

                print(f"\n{'=' * 60}")
                print(f"{prefab}: {len(objects)} found")
                print('=' * 60)

                for idx, obj in enumerate(objects):
                    info = extract_geyser_info(obj)
                    print(format_geyser_output(prefab, idx, info, debug=args.debug))

                total_count += len(objects)

            print(f"\n{'=' * 60}")
            print(f"Total geysers: {total_count}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
