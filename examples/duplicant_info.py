"""Extract and display duplicant information from ONI save files.

This script loads a save file and prints detailed information about duplicants
including their name, traits, skills, stress, health, and current activities.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract duplicant information from ONI save files"
    )
    parser.add_argument("save_file", type=Path, help="Path to .sav file")

    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
