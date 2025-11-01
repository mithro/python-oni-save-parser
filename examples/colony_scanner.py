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


def scan_save_files(
    directory: Path,
    recursive: bool = True,
    stream_output: bool = False,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Scan directory for save files and extract colony info.

    Args:
        directory: Directory to scan
        recursive: If True, scan subdirectories recursively
        stream_output: If True, print results as they're found
        limit: If set, only process this many save files (for testing)

    Returns:
        List of dictionaries with colony information
    """
    import time
    from collections import Counter

    colonies = []

    # Find all .sav files (recursively or not) - convert to list for counting
    if recursive:
        all_save_paths = [p for p in directory.rglob("*.sav") if "auto_save" not in p.parts]
    else:
        all_save_paths = [p for p in directory.glob("*.sav") if "auto_save" not in p.parts]

    all_save_paths = sorted(all_save_paths)
    total_files = len(all_save_paths)

    # Apply limit if specified
    if limit is not None and limit > 0:
        all_save_paths = all_save_paths[:limit]

    # Count files per colony directory
    colony_file_counts: dict[str, int] = Counter()
    for p in all_save_paths:
        try:
            rel_path = p.relative_to(directory)
            colony_dir = str(rel_path.parent) if rel_path.parent != Path(".") else "."
            colony_file_counts[colony_dir] += 1
        except ValueError:
            colony_file_counts[str(p.parent)] += 1

    # Calculate width for progress display (based on max values)
    max_colony_count = max(colony_file_counts.values()) if colony_file_counts else 0
    total_width = len(str(total_files))
    colony_width = len(str(max_colony_count))

    # Print header if streaming
    if stream_output:
        print(f"Found {total_files} save files to scan...\n")
        print(
            f"{'Colony Name':<30} {'Cycle':>6} {'Dups':>5} {'Time':>6} "
            f"{'Progress':<20} {'Path':<25} {'File':<25}"
        )
        print("-" * 140)
        sys.stdout.flush()

    current_colony_counts: dict[str, int] = Counter()

    for idx, save_path in enumerate(all_save_paths, 1):
        try:
            # Get relative path for progress tracking
            try:
                rel_path = save_path.relative_to(directory)
                path_str = str(rel_path.parent) if rel_path.parent != Path(".") else "."
            except ValueError:
                path_str = str(save_path.parent)

            current_colony_counts[path_str] += 1

            # Time the load operation
            start_time = time.time()
            save = load_save_file(save_path)
            info = get_colony_info(save)
            load_time = time.time() - start_time

            # Get file modification time
            mtime = datetime.fromtimestamp(save_path.stat().st_mtime)

            colony_info = {
                "file": save_path.name,
                "path": path_str,
                "colony_name": info["colony_name"],
                "cycle": info["cycle"],
                "duplicants": info["duplicant_count"],
                "modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "cluster": info["cluster_id"],
                "load_time": load_time,
            }

            colonies.append(colony_info)

            # Print immediately if streaming
            if stream_output:
                path_display = colony_info['path'] if colony_info['path'] else "."
                # Fixed-width progress string: "   9/2804,  8/48" -> "1802/2804, 40/48"
                colony_current = current_colony_counts[path_str]
                colony_total = colony_file_counts[path_str]
                progress_str = (
                    f"{idx:>{total_width}}/{total_files}, "
                    f"{colony_current:>{colony_width}}/{colony_total}"
                )

                print(
                    f"{colony_info['colony_name']:<30} "
                    f"{colony_info['cycle']:>6} "
                    f"{colony_info['duplicants']:>5} "
                    f"{load_time:>6.2f}s "
                    f"{progress_str:<20} "
                    f"{path_display:<25} "
                    f"{colony_info['file']:<25}"
                )
                sys.stdout.flush()

        except Exception as e:
            # Skip files that can't be parsed
            print(f"Warning: Could not parse {save_path}: {e}", file=sys.stderr)
            sys.stderr.flush()
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
    print(
        f"{'Colony Name':<30} {'Cycle':>6} {'Dups':>5} "
        f"{'Modified':<19} {'Path':<30} {'File':<30}"
    )
    print("-" * 130)

    # Print each colony
    for colony in colonies:
        path_display = colony['path'] if colony['path'] else "."
        print(
            f"{colony['colony_name']:<30} "
            f"{colony['cycle']:>6} "
            f"{colony['duplicants']:>5} "
            f"{colony['modified']:<19} "
            f"{path_display:<30} "
            f"{colony['file']:<30}"
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
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories (default: recursive)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=argparse.SUPPRESS,  # Hidden argument for testing
    )

    args = parser.parse_args()

    # Use default directory if not specified
    save_dir = args.directory if args.directory else get_default_save_directory()

    if not save_dir.exists():
        print(f"Error: Directory not found: {save_dir}", file=sys.stderr)
        return 1

    # Scan for save files
    recursive = not args.no_recursive

    # Use streaming output for text mode, buffered for JSON
    if args.json:
        colonies = scan_save_files(
            save_dir, recursive=recursive, stream_output=False, limit=args.limit
        )
        print(json.dumps(colonies, indent=2))
    else:
        colonies = scan_save_files(
            save_dir, recursive=recursive, stream_output=True, limit=args.limit
        )
        print(f"\nTotal: {len(colonies)} save files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
