"""Count resources in ONI save files.

This script analyzes storage containers, loose debris, and duplicant inventories
to provide a comprehensive inventory of all resources in your colony.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from oni_save_parser import load_save_file

# Storage container prefab names
STORAGE_PREFABS = {
    "StorageLocker",
    "LiquidReservoir",
    "GasReservoir",
    "StorageLockerSmart",
    "LiquidReservoirSmart",
    "GasReservoirSmart",
}

# Prefabs to exclude from debris detection (handled separately or not relevant)
DEBRIS_EXCLUSIONS = STORAGE_PREFABS | {"Minion"}  # Minions handled by duplicant inventory function


def find_storage_containers(save: Any) -> list[dict[str, Any]]:
    """Find all items stored in storage containers."""
    stored_items = []

    for group in save.game_objects:
        if group.prefab_name in STORAGE_PREFABS:
            for obj in group.objects:
                # Look for Storage behavior with stored items
                for behavior in obj.behaviors:
                    if behavior.name == "Storage" and behavior.extra_data:
                        # extra_data is list of stored GameObjects
                        for stored_obj in behavior.extra_data:
                            # Extract mass from stored item's PrimaryElement
                            for stored_behavior in stored_obj.get("behaviors", []):
                                if stored_behavior.name == "PrimaryElement":
                                    # Real saves use "Units", test fixtures use "Mass"
                                    mass = stored_behavior.template_data.get(
                                        "Units"
                                    ) or stored_behavior.template_data.get("Mass", 0.0)
                                    if mass > 0:
                                        stored_items.append(
                                            {
                                                "prefab": stored_obj.get("name", "Unknown"),
                                                "mass": mass,
                                                "position": (obj.position.x, obj.position.y),
                                                "container": group.prefab_name,
                                            }
                                        )
    return stored_items


def find_debris(save: Any) -> list[dict[str, Any]]:
    """Find loose debris (pickupable objects).

    Follows design spec: Find objects with Pickupable component,
    extract PrimaryElement data. Filters out storage containers.
    Buildings/plants don't have Pickupable, so they're naturally excluded.
    """
    debris_items = []

    for group in save.game_objects:
        # Skip excluded prefabs (storage containers, minions, etc.)
        if group.prefab_name in DEBRIS_EXCLUSIONS:
            continue

        for obj in group.objects:
            # Design spec: Find objects with Pickupable component
            # Extract mass from PrimaryElement
            has_pickupable = False
            primary_element = None
            is_creature = False

            for behavior in obj.behaviors:
                if behavior.name == "Pickupable":
                    has_pickupable = True
                elif behavior.name == "PrimaryElement":
                    primary_element = behavior
                elif behavior.name == "CreatureBrain":
                    is_creature = True

            # Skip creatures (WoodDeer, Hatch, etc.) - they're not debris
            if is_creature:
                continue

            # Only count if it has BOTH Pickupable AND PrimaryElement
            # Real saves properly mark debris with Pickupable behavior
            # Buildings/plants have PrimaryElement but NOT Pickupable
            if has_pickupable and primary_element:
                # Real saves use "Units", test fixtures use "Mass"
                mass = primary_element.template_data.get(
                    "Units"
                ) or primary_element.template_data.get("Mass", 0.0)
                if mass > 0:
                    debris_items.append(
                        {
                            "prefab": group.prefab_name,
                            "mass": mass,
                            "position": (obj.position.x, obj.position.y),
                        }
                    )

    return debris_items


def find_duplicant_inventories(save: Any) -> list[dict[str, Any]]:
    """Find resources carried by duplicants.

    Scans Minion objects for Storage behavior with carried items.
    """
    duplicant_items = []

    for group in save.game_objects:
        if group.prefab_name == "Minion":
            for obj in group.objects:
                # Find MinionIdentity for duplicant name
                minion_name = "Unknown"
                for behavior in obj.behaviors:
                    if behavior.name == "MinionIdentity":
                        minion_name = behavior.template_data.get("name", "Unknown")
                        break

                # Find Storage behavior for carried items
                for behavior in obj.behaviors:
                    if behavior.name == "Storage" and behavior.extra_data:
                        # extra_data is list of carried GameObjects
                        for carried_obj in behavior.extra_data:
                            # Extract mass from carried item's PrimaryElement
                            for carried_behavior in carried_obj.get("behaviors", []):
                                if carried_behavior.name == "PrimaryElement":
                                    # Real saves use "Units", test fixtures use "Mass"
                                    mass = carried_behavior.template_data.get(
                                        "Units"
                                    ) or carried_behavior.template_data.get("Mass", 0.0)
                                    if mass > 0:
                                        duplicant_items.append(
                                            {
                                                "duplicant": minion_name,
                                                "prefab": carried_obj.get("name", "Unknown"),
                                                "mass": mass,
                                                "position": (obj.position.x, obj.position.y),
                                            }
                                        )

    return duplicant_items


def apply_filters(
    containers: list[dict[str, Any]],
    debris: list[dict[str, Any]],
    duplicants: list[dict[str, Any]],
    element_filter: str | None = None,
    min_mass: float | None = None,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Apply element and mass filters to resource lists."""
    filtered_containers = containers
    filtered_debris = debris
    filtered_duplicants = duplicants

    # Apply element filter (filter by prefab name)
    if element_filter:
        filtered_containers = [c for c in filtered_containers if c["prefab"] == element_filter]
        filtered_debris = [d for d in filtered_debris if d["prefab"] == element_filter]
        # Duplicants don't have prefab field, so we skip filtering them by element

    # Apply minimum mass filter
    if min_mass is not None:
        filtered_containers = [c for c in filtered_containers if c["mass"] >= min_mass]
        filtered_debris = [d for d in filtered_debris if d["mass"] >= min_mass]
        filtered_duplicants = [d for d in filtered_duplicants if d["mass"] >= min_mass]

    return filtered_containers, filtered_debris, filtered_duplicants


def get_all_element_names(
    containers: list[dict[str, Any]], debris: list[dict[str, Any]]
) -> set[str]:
    """Get all unique prefab names from containers and debris."""
    element_names = set()
    for item in containers:
        element_names.add(item["prefab"])
    for item in debris:
        element_names.add(item["prefab"])
    return element_names


def aggregate_by_element(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Aggregate items by element type with statistics.

    Args:
        items: List of items with 'prefab' and 'mass' fields

    Returns:
        Dictionary mapping prefab name to aggregated stats
    """
    aggregated: dict[str, dict[str, Any]] = {}

    for item in items:
        prefab = item["prefab"]
        mass = item["mass"]

        if prefab not in aggregated:
            aggregated[prefab] = {
                "count": 0,
                "total_mass": 0.0,
                "min_mass": float("inf"),
                "max_mass": 0.0,
            }

        stats = aggregated[prefab]
        stats["count"] += 1
        stats["total_mass"] += mass
        stats["min_mass"] = min(stats["min_mass"], mass)
        stats["max_mass"] = max(stats["max_mass"], mass)

    return aggregated


def format_summary_output(
    containers: list[dict[str, Any]], debris: list[dict[str, Any]], duplicants: list[dict[str, Any]]
) -> str:
    """Format resources as aggregated summary by element type."""
    lines = []

    # Storage section - aggregated by element
    if containers:
        lines.append("\nSTORAGE CONTAINERS (by element):")
        lines.append(f"{'Element':<25} {'Count':>8} {'Total Mass':>15} {'Avg Mass':>12}")
        lines.append("-" * 62)

        agg = aggregate_by_element(containers)
        for prefab in sorted(agg.keys()):
            stats = agg[prefab]
            avg_mass = stats["total_mass"] / stats["count"]
            total_str = f"{stats['total_mass']:.1f} kg"
            avg_str = f"{avg_mass:.1f} kg"
            lines.append(f"{prefab:<25} {stats['count']:>8} {total_str:>15} {avg_str:>12}")

        total_mass = sum(c["mass"] for c in containers)
        lines.append(f"\nTotal: {len(containers)} items in storage, {total_mass:.1f} kg")

    # Debris section - aggregated by element
    if debris:
        lines.append("\nDEBRIS (by element):")
        lines.append(f"{'Element':<25} {'Piles':>8} {'Total Mass':>15} {'Avg/pile':>12}")
        lines.append("-" * 62)

        agg = aggregate_by_element(debris)
        for prefab in sorted(agg.keys()):
            stats = agg[prefab]
            avg_mass = stats["total_mass"] / stats["count"]
            total_str = f"{stats['total_mass']:.1f} kg"
            avg_str = f"{avg_mass:.1f} kg"
            lines.append(f"{prefab:<25} {stats['count']:>8} {total_str:>15} {avg_str:>12}")

        total_mass = sum(d["mass"] for d in debris)
        lines.append(f"\nTotal: {len(debris)} debris piles, {total_mass:.1f} kg")

    # Duplicants section - show individuals (usually small count)
    if duplicants:
        lines.append("\nDUPLICANTS CARRYING:")
        lines.append(f"{'Duplicant':<20} {'Item':<25} {'Mass':>12}")
        lines.append("-" * 59)
        for item in duplicants:
            prefab = item.get("prefab", "Unknown")
            mass_str = f"{item['mass']:.1f} kg"
            lines.append(f"{item['duplicant']:<20} {prefab:<25} {mass_str:>12}")

        total_mass = sum(d["mass"] for d in duplicants)
        lines.append(f"\nTotal: {len(duplicants)} items carried, {total_mass:.1f} kg")

    if not containers and not debris and not duplicants:
        lines.append("\nNo resources found")

    return "\n".join(lines)


def format_detailed_output(
    containers: list[dict[str, Any]], debris: list[dict[str, Any]], duplicants: list[dict[str, Any]]
) -> str:
    """Format resources with all individual items listed."""
    lines = []

    # Storage section
    if containers:
        lines.append("\nSTORAGE CONTAINERS:")
        lines.append(f"{'Prefab':<20} {'Mass (kg)':>12} {'Position':>20}")
        lines.append("-" * 53)
        for item in containers:
            pos_str = f"({item['position'][0]:.1f}, {item['position'][1]:.1f})"
            lines.append(f"{item['prefab']:<20} {item['mass']:>12.1f} {pos_str:>20}")
        total_mass = sum(c["mass"] for c in containers)
        lines.append(f"\nTotal: {len(containers)} containers, {total_mass:.1f} kg")

    # Debris section
    if debris:
        lines.append("\nDEBRIS ITEMS:")
        lines.append(f"{'Prefab':<20} {'Mass (kg)':>12} {'Position':>20}")
        lines.append("-" * 53)
        for item in debris:
            pos_str = f"({item['position'][0]:.1f}, {item['position'][1]:.1f})"
            lines.append(f"{item['prefab']:<20} {item['mass']:>12.1f} {pos_str:>20}")
        lines.append(f"\nTotal: {len(debris)} items, {sum(d['mass'] for d in debris):.1f} kg")

    # Duplicants section
    if duplicants:
        lines.append("\nDUPLICANTS CARRYING ITEMS:")
        lines.append(f"{'Name':<20} {'Item':<20} {'Mass (kg)':>12} {'Position':>20}")
        lines.append("-" * 73)
        for item in duplicants:
            pos_str = f"({item['position'][0]:.1f}, {item['position'][1]:.1f})"
            prefab = item.get("prefab", "Unknown")
            lines.append(
                f"{item['duplicant']:<20} {prefab:<20} {item['mass']:>12.1f} {pos_str:>20}"
            )
        total_mass = sum(d["mass"] for d in duplicants)
        lines.append(f"\nTotal: {len(duplicants)} items carried, {total_mass:.1f} kg")

    if not containers and not debris and not duplicants:
        lines.append("\nNo resources found")

    return "\n".join(lines)


def format_json_output(
    containers: list[dict[str, Any]], debris: list[dict[str, Any]], duplicants: list[dict[str, Any]]
) -> str:
    """Format resources as JSON with comprehensive details."""
    output = {
        "storage": containers,
        "debris": debris,
        "duplicants": duplicants,
        "summary": {
            "total_storage_containers": len(containers),
            "total_debris_items": len(debris),
            "total_duplicants_carrying": len(duplicants),
        },
    }
    return json.dumps(output, indent=2)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files by location and element type"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file", nargs="?")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show individual items with positions (default: summary by element)",
    )
    parser.add_argument(
        "--element",
        type=str,
        help="Filter by prefab name (e.g., IronOre, StorageLocker)",
    )
    parser.add_argument("--min-mass", type=float, help="Filter out items below this mass (kg)")
    parser.add_argument(
        "--list-elements",
        action="store_true",
        help="List all prefab types found and exit",
    )

    args = parser.parse_args()

    # --list-elements doesn't require save_file, but everything else does
    if not args.list_elements and not args.save_file:
        parser.error("save_file is required unless using --list-elements")

    if args.save_file and not args.save_file.exists():
        print(f"Error: File not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        save = load_save_file(args.save_file)
        containers = find_storage_containers(save)
        debris = find_debris(save)
        duplicants = find_duplicant_inventories(save)

        # Handle --list-elements flag
        if args.list_elements:
            element_names = get_all_element_names(containers, debris)
            if element_names:
                print("\nPrefab types found:")
                for name in sorted(element_names):
                    print(f"  {name}")
                print(f"\nTotal: {len(element_names)} prefab types")
            else:
                print("\nNo prefab types found")
            return 0

        # Apply filters
        containers, debris, duplicants = apply_filters(
            containers, debris, duplicants, element_filter=args.element, min_mass=args.min_mass
        )

        if args.json:
            print(format_json_output(containers, debris, duplicants))
        elif args.verbose:
            print(format_detailed_output(containers, debris, duplicants))
        else:
            print(format_summary_output(containers, debris, duplicants))

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
