#!/usr/bin/env python3
"""Scan ONI save directories and display colony status table.

This script scans a directory for ONI save files and displays a table showing:
- Colony name
- Current cycle
- Number of duplicants
- Save file name
- Last modified date
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from oni_save_parser import get_colony_info, load_save_file


def get_default_save_directory() -> Path:
    """Get the default ONI save directory path.

    Returns:
        Path to ONI cloud save files directory
    """
    return Path.home() / ".config/unity3d/Klei/Oxygen Not Included/cloud_save_files"


def scan_save_files(directory: Path) -> list[dict[str, Any]]:
    """Scan directory for save files and extract colony info.

    Args:
        directory: Directory to scan

    Returns:
        List of dictionaries with colony information
    """
    colonies = []

    # Find all .sav files
    for save_path in sorted(directory.glob("*.sav")):
        try:
            # Load and extract colony info
            save = load_save_file(save_path)
            info = get_colony_info(save)

            # Get file modification time
            mtime = datetime.fromtimestamp(save_path.stat().st_mtime)

            colonies.append({
                "file": save_path.name,
                "colony_name": info["colony_name"],
                "cycle": info["cycle"],
                "duplicants": info["duplicant_count"],
                "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "cluster": info["cluster_id"],
            })
        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not parse {save_path.name}: {e}", file=sys.stderr)
            continue

    return colonies


def print_table(colonies: list[dict[str, Any]]) -> None:
    """Print colonies as a formatted table.

    Args:
        colonies: List of colony information dictionaries
    """
    if not colonies:
        print("No save files found.")
        return

    # Print header
    print(f"{'Colony Name':<30} {'Cycle':>6} {'Dups':>5} {'Modified':<19} {'File':<40}")
    print("-" * 110)

    # Print each colony
    for colony in colonies:
        print(
            f"{colony['colony_name']:<30} "
            f"{colony['cycle']:>6} "
            f"{colony['duplicants']:>5} "
            f"{colony['modified']:<19} "
            f"{colony['file']:<40}"
        )

    print(f"\nTotal: {len(colonies)} save files")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Scan ONI save directories and display colony status"
    )
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=None,
        help="Directory to scan for save files (default: ONI cloud_save_files)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of table",
    )

    args = parser.parse_args()

    # Use default directory if not specified
    save_dir = args.directory if args.directory else get_default_save_directory()

    if not save_dir.exists():
        print(f"Error: Directory not found: {save_dir}", file=sys.stderr)
        return 1

    # Scan for save files
    colonies = scan_save_files(save_dir)

    # Output results
    if args.json:
        print(json.dumps(colonies, indent=2))
    else:
        print_table(colonies)

    return 0


if __name__ == "__main__":
    sys.exit(main())
