"""Command-line interface for ONI Save Parser."""

import argparse
import json
import sys
from pathlib import Path

from oni_save_parser import (
    get_colony_info,
    get_prefab_counts,
    list_prefab_types,
    load_save_file,
)


def cmd_info(args: argparse.Namespace) -> int:
    """Display colony information."""
    try:
        save = load_save_file(args.file, allow_minor_mismatch=args.allow_minor_mismatch)
        info = get_colony_info(save)

        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print(f"Colony: {info['colony_name']}")
            print(f"Cycle: {info['cycle']}")
            print(f"Duplicants: {info['duplicant_count']}")
            print(f"Cluster: {info['cluster_id']}")
            print(f"DLC: {info['dlc_id'] or 'None'}")
            print(f"Save Version: {info['save_version']}")
            print(f"Build Version: {info['build_version']}")
            print(f"Compressed: {info['compressed']}")
            print(f"Sandbox: {info['sandbox_enabled']}")
            print(f"Auto Save: {info['is_auto_save']}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_prefabs(args: argparse.Namespace) -> int:
    """List prefab types."""
    try:
        save = load_save_file(args.file, allow_minor_mismatch=args.allow_minor_mismatch)

        if args.counts:
            counts = get_prefab_counts(save)
            if args.json:
                print(json.dumps(counts, indent=2))
            else:
                for prefab, count in sorted(counts.items()):
                    print(f"{prefab}: {count}")
        else:
            prefabs = list_prefab_types(save)
            if args.json:
                print(json.dumps(prefabs, indent=2))
            else:
                for prefab in sorted(prefabs):
                    print(prefab)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="oni-save-parser",
        description="Parse and analyze Oxygen Not Included save files",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.4.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # info command
    info_parser = subparsers.add_parser("info", help="Display colony information")
    info_parser.add_argument("file", type=Path, help="Path to .sav file")
    info_parser.add_argument("--json", action="store_true", help="Output as JSON")
    info_parser.add_argument(
        "--allow-minor-mismatch",
        action="store_true",
        default=True,
        help="Allow minor version mismatches (default: True)",
    )
    info_parser.set_defaults(func=cmd_info)

    # prefabs command
    prefabs_parser = subparsers.add_parser("prefabs", help="List prefab types")
    prefabs_parser.add_argument("file", type=Path, help="Path to .sav file")
    prefabs_parser.add_argument("--counts", action="store_true", help="Show object counts")
    prefabs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    prefabs_parser.add_argument(
        "--allow-minor-mismatch",
        action="store_true",
        default=True,
        help="Allow minor version mismatches (default: True)",
    )
    prefabs_parser.set_defaults(func=cmd_prefabs)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
