#!/usr/bin/env python3
"""Basic usage examples for ONI Save Parser.

This script demonstrates common use cases for the ONI save parser library.
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from oni_save_parser import (
    get_colony_info,
    get_game_objects_by_prefab,
    get_prefab_counts,
    list_prefab_types,
    load_save_file,
    save_to_file,
)


def example_load_and_display_info(save_path: str) -> None:
    """Load a save file and display colony information."""
    print("=" * 60)
    print("Example 1: Load and Display Colony Info")
    print("=" * 60)

    save = load_save_file(save_path)
    info = get_colony_info(save)

    print(f"\nColony: {info['colony_name']}")
    print(f"Cycle: {info['cycle']}")
    print(f"Duplicants: {info['duplicant_count']}")
    print(f"Cluster: {info['cluster_id']}")
    print(f"DLC: {info['dlc_id'] or 'Base Game'}")
    print(f"Save Version: {info['save_version']}")
    print(f"Compressed: {info['compressed']}")
    print(f"Sandbox: {info['sandbox_enabled']}")


def example_list_prefabs(save_path: str) -> None:
    """List all prefab types and their counts."""
    print("\n" + "=" * 60)
    print("Example 2: List Prefab Types and Counts")
    print("=" * 60)

    save = load_save_file(save_path)
    prefabs = list_prefab_types(save)
    counts = get_prefab_counts(save)

    print(f"\nTotal prefab types: {len(prefabs)}")
    print(f"Total objects: {sum(counts.values())}")

    print("\nTop 10 most common objects:")
    for prefab, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {prefab}: {count}")


def example_analyze_duplicants(save_path: str) -> None:
    """Analyze duplicant information."""
    print("\n" + "=" * 60)
    print("Example 3: Analyze Duplicants")
    print("=" * 60)

    save = load_save_file(save_path)
    minions = get_game_objects_by_prefab(save, "Minion")

    print(f"\nFound {len(minions)} duplicants:")

    for i, minion in enumerate(minions, 1):
        print(f"\nDuplicant #{i}:")
        print(f"  Position: ({minion.position.x:.1f}, {minion.position.y:.1f}, {minion.position.z:.1f})")

        # Find MinionIdentity behavior
        for behavior in minion.behaviors:
            if behavior.name == "MinionIdentity" and behavior.template_data:
                name = behavior.template_data.get("name", "Unknown")
                print(f"  Name: {name}")

            if behavior.name == "Health" and behavior.template_data:
                hp = behavior.template_data.get("hitpoints", 0)
                max_hp = behavior.template_data.get("maxHitpoints", 100)
                print(f"  Health: {hp:.1f}/{max_hp:.1f}")

            if behavior.name == "MinionResume" and behavior.template_data:
                total_exp = behavior.template_data.get("totalExperienceGained", 0)
                print(f"  Experience: {total_exp}")


def example_modify_save(save_path: str) -> None:
    """Modify a save file and write it back."""
    print("\n" + "=" * 60)
    print("Example 4: Modify Save File")
    print("=" * 60)

    save = load_save_file(save_path)

    # Modify colony name
    original_name = save.header.game_info.base_name
    new_name = f"{original_name} (Modified)"
    save.header.game_info.base_name = new_name

    print(f"\nOriginal colony name: {original_name}")
    print(f"New colony name: {new_name}")

    # Write to a new file
    output_path = Path(save_path).parent / f"{Path(save_path).stem}_modified.sav"
    save_to_file(save, output_path)
    print(f"\nModified save written to: {output_path}")

    # Verify the change
    modified_save = load_save_file(output_path)
    print(f"Verified new name: {modified_save.header.game_info.base_name}")


def example_analyze_buildings(save_path: str) -> None:
    """Analyze building distribution."""
    print("\n" + "=" * 60)
    print("Example 5: Analyze Buildings")
    print("=" * 60)

    save = load_save_file(save_path)
    counts = get_prefab_counts(save)

    # Define building categories
    power_buildings = ["Generator", "Battery", "Wire", "Transformer"]
    plumbing = ["Pipe", "Pump", "Valve", "Reservoir"]
    ventilation = ["Vent", "Fan"]
    food = ["Farm", "Kitchen", "Refrigerator"]

    print("\nBuilding Categories:")

    for category_name, keywords in [
        ("Power", power_buildings),
        ("Plumbing", plumbing),
        ("Ventilation", ventilation),
        ("Food", food),
    ]:
        count = sum(v for k, v in counts.items() if any(keyword in k for keyword in keywords))
        print(f"  {category_name}: {count} buildings")


def main():
    """Run all examples."""
    import argparse

    parser = argparse.ArgumentParser(description="ONI Save Parser Examples")
    parser.add_argument("save_file", type=str, help="Path to .sav file")
    parser.add_argument(
        "--example",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific example only (1-5)",
    )

    args = parser.parse_args()

    if not Path(args.save_file).exists():
        print(f"Error: Save file not found: {args.save_file}", file=sys.stderr)
        return 1

    try:
        if args.example is None or args.example == 1:
            example_load_and_display_info(args.save_file)

        if args.example is None or args.example == 2:
            example_list_prefabs(args.save_file)

        if args.example is None or args.example == 3:
            example_analyze_duplicants(args.save_file)

        if args.example is None or args.example == 4:
            example_modify_save(args.save_file)

        if args.example is None or args.example == 5:
            example_analyze_buildings(args.save_file)

        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("=" * 60)

        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
