"""Count resources in ONI save files.

This script analyzes storage containers, loose debris, and duplicant inventories
to provide a comprehensive inventory of all resources in your colony.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Count resources in ONI save files by location and element type"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
