#!/usr/bin/env python3
"""CLI tool for rendering ONI save files to images."""
import argparse
from pathlib import Path

from oni_save_parser.rendering.pipeline import MapRenderer


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Render ONI save files to PNG images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render all asteroids from a save
  %(prog)s save.sav --output-dir renders/

  # Render with larger scale
  %(prog)s save.sav --output-dir renders/ --scale 4
        """,
    )

    parser.add_argument(
        "save_path",
        type=Path,
        help="Path to .sav file",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("renders"),
        help="Output directory for PNG files (default: renders/)",
    )

    parser.add_argument(
        "--scale",
        type=int,
        default=2,
        choices=range(1, 11),
        help="Pixels per tile, 1-10 (default: 2)",
    )

    args = parser.parse_args()

    # Validate save file exists
    if not args.save_path.exists():
        print(f"Error: Save file not found: {args.save_path}")
        return

    # Render
    print(f"Rendering {args.save_path}...")
    print(f"Output directory: {args.output_dir}")
    print(f"Scale: {args.scale}x")

    renderer = MapRenderer()
    output_files = renderer.render(
        save_path=args.save_path,
        output_dir=args.output_dir,
        scale=args.scale,
    )

    print(f"\nRendered {len(output_files)} asteroid(s):")
    for file_path in output_files:
        print(f"  {file_path}")


if __name__ == "__main__":
    main()
